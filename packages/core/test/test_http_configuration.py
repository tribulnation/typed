"""Exercise HTTPX timeout and proxy selection through the managed transport."""

from typing_extensions import Any
import httpx
import pytest

from typed_core.http import HttpClient
from typed_core.exceptions import NetworkError

pytestmark = pytest.mark.asyncio


@pytest.fixture
def routes(monkeypatch: pytest.MonkeyPatch):
  """Replace network I/O while retaining HTTPX request construction and routing."""
  for name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY'):
    monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv(name.lower(), raising=False)
  monkeypatch.delenv('SSL_CERT_FILE', raising=False)
  monkeypatch.delenv('SSL_CERT_DIR', raising=False)
  records: list[tuple[httpx.Proxy | None, httpx.Request]] = []
  transports: list[httpx.AsyncBaseTransport] = []

  class RecordingTransport(httpx.AsyncBaseTransport):
    """Record the selected proxy and fully constructed request without networking."""

    def __init__(self, *, proxy: httpx.Proxy | None = None, **kwargs: Any):
      """Capture transport settings passed by the real HTTPX client."""
      self.proxy = proxy
      self.settings = kwargs
      self.closes = 0
      transports.append(self)

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
      """Return a response, or simulate one read timeout."""
      records.append((self.proxy, request))
      if request.url.path == '/timeout':
        raise httpx.ReadTimeout('timed out', request=request)
      return httpx.Response(200, json={'ok': True})

    async def aclose(self):
      """Count closures of the underlying transport."""
      self.closes += 1

  monkeypatch.setattr(httpx._client, 'AsyncHTTPTransport', RecordingTransport)
  return records, transports


@pytest.mark.parametrize('timeout', [5.0, 120.0, None, httpx.Timeout(30, connect=2)])
async def test_timeout_inheritance_and_override(routes, timeout):
  """Every request inherits its client default unless explicitly overridden."""
  records, _ = routes
  async with HttpClient(timeout=timeout) as http:
    await http.request('GET', 'https://service.test/default')
    await http.request('GET', 'https://service.test/override', timeout=9)
    await http.request('GET', 'https://service.test/disabled', timeout=None)
  assert records[0][1].extensions['timeout'] == httpx.Timeout(timeout).as_dict()
  assert records[1][1].extensions['timeout'] == httpx.Timeout(9).as_dict()
  assert records[2][1].extensions['timeout'] == httpx.Timeout(None).as_dict()


async def test_default_timeout_and_lazy_lifecycle(routes):
  """Defaults remain five seconds; the transport opens lazily and closes once."""
  records, transports = routes
  async with HttpClient() as http:
    assert not transports
    await http.request('GET', 'https://service.test')
    await http.request('GET', 'https://service.test')
  assert records[0][1].extensions['timeout'] == httpx.Timeout(5).as_dict()
  assert len(transports) == 1
  assert transports[0].closes == 1


@pytest.mark.parametrize('lowercase', [False, True])
async def test_environment_proxy_routing(routes, monkeypatch, lowercase):
  """HTTP, HTTPS, fallback, and bypass variables retain HTTPX semantics."""
  values = {
    'HTTP_PROXY': 'http://http-proxy.test:8000',
    'HTTPS_PROXY': 'http://https-proxy.test:8001',
    'NO_PROXY': 'direct.test',
  }
  for name, value in values.items():
    monkeypatch.setenv(name.lower() if lowercase else name, value)
  records, _ = routes
  async with HttpClient() as http:
    await http.request('GET', 'http://service.test')
    await http.request('GET', 'https://service.test')
    await http.request('GET', 'https://direct.test')
  assert str(records[0][0].url) == values['HTTP_PROXY']
  assert str(records[1][0].url) == values['HTTPS_PROXY']
  assert records[2][0] is None
  monkeypatch.delenv('HTTPS_PROXY'.lower() if lowercase else 'HTTPS_PROXY')
  monkeypatch.setenv('ALL_PROXY', 'http://fallback.test:8002')
  async with HttpClient() as http:
    await http.request('GET', 'https://service.test')
  assert str(records[-1][0].url) == 'http://fallback.test:8002'


@pytest.mark.parametrize(
  'proxy', ['http://explicit.test:8000', httpx.Proxy('https://explicit.test:8000')]
)
@pytest.mark.parametrize('trust_env', [False, True])
async def test_explicit_proxy_overrides_environment(
  routes, monkeypatch, proxy, trust_env
):
  """An explicit proxy wins even when NO_PROXY would bypass an environment proxy."""
  monkeypatch.setenv('HTTPS_PROXY', 'http://environment.test:8001')
  monkeypatch.setenv('NO_PROXY', 'service.test')
  records, _ = routes
  async with HttpClient(proxy=proxy, trust_env=trust_env) as http:
    await http.request('GET', 'https://service.test')
    await http.request('GET', 'http://service.test')
  expected = proxy.url if isinstance(proxy, httpx.Proxy) else httpx.URL(proxy)
  assert all(selected.url == expected for selected, _ in records)


async def test_ignore_environment_and_preserve_limits(routes, monkeypatch):
  """Opting out ignores proxies while explicit connection limits still reach HTTPX."""
  monkeypatch.setenv('ALL_PROXY', 'http://environment.test:8000')
  records, transports = routes
  limits = httpx.Limits(max_connections=7)
  async with HttpClient(trust_env=False, limits=limits) as http:
    await http.request('GET', 'https://service.test')
  assert records[0][0] is None
  assert transports[0].settings['limits'] is limits


async def test_injected_raw_client_retains_its_configuration(routes):
  """Legacy raw-client injection remains usable and keeps its own settings."""
  records, _ = routes
  raw = httpx.AsyncClient(timeout=42, trust_env=False)
  async with HttpClient(_client=raw, timeout=3, proxy='http://unused.test') as http:
    await http.request('GET', 'https://service.test')
  assert records[0][0] is None
  assert records[0][1].extensions['timeout'] == httpx.Timeout(42).as_dict()
  assert raw.is_closed


async def test_transport_failure_is_not_retried(routes):
  """Configuration does not introduce retries or alter NetworkError mapping."""
  records, _ = routes
  async with HttpClient() as http:
    with pytest.raises(NetworkError, match='ReadTimeout'):
      await http.request('GET', 'https://service.test/timeout')
  assert len(records) == 1


async def test_proxy_credentials_hidden_from_repr():
  """The transport representation omits proxy credentials."""
  assert 'secret' not in repr(HttpClient(proxy='http://user:secret@proxy.test'))
