"""Idle keep-alive of the managed HTTP pool against a real local HTTP/1.1 server."""

import asyncio
import time
from types import SimpleNamespace

import httpx
import pytest

from typed_core.http import KEEPALIVE_EXPIRY, HttpClient

RESPONSE = b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\nContent-Type: text/plain\r\n\r\nok'


def advance_pool_clock(monkeypatch: pytest.MonkeyPatch, seconds: float):
  """Make HTTPX's connection pool see `seconds` more of idle time than has passed."""
  now = time.monotonic()
  clock = SimpleNamespace(monotonic=lambda: now + seconds)
  monkeypatch.setattr('httpcore._async.http11.time', clock)


@pytest.fixture(autouse=True)
def no_proxy_environment(monkeypatch: pytest.MonkeyPatch):
  """Run without environment proxies, so the default limits apply to loopback."""
  for name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY'):
    monkeypatch.delenv(name, raising=False)
    monkeypatch.delenv(name.lower(), raising=False)


class Server:
  """Minimal keep-alive HTTP/1.1 server counting the connections it accepts."""

  def __init__(self, *, idle_close: float | None = None):
    """
    Args:
      idle_close: Close a connection this many seconds after each response, as a server
        idle timeout would; `None` keeps it open.
    """
    self.idle_close = idle_close
    self.connections = 0
    self.server: asyncio.Server | None = None

  async def handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    """Answer each request on the connection until the client leaves or it idles out."""
    self.connections += 1
    try:
      while await reader.readuntil(b'\r\n\r\n'):
        writer.write(RESPONSE)
        await writer.drain()
        if self.idle_close is not None:
          await asyncio.sleep(self.idle_close)
          break
    except asyncio.IncompleteReadError:
      pass
    finally:
      writer.close()

  async def __aenter__(self):
    """Listen on an ephemeral loopback port."""
    self.server = await asyncio.start_server(self.handle, '127.0.0.1', 0)
    return self

  async def __aexit__(self, *args):
    """Stop listening."""
    assert self.server is not None
    self.server.close()

  @property
  def url(self) -> str:
    """Base URL of the server."""
    assert self.server is not None
    host, port = self.server.sockets[0].getsockname()[:2]
    return f'http://{host}:{port}/'


def test_default_keeps_idle_connections():
  """Idle connections stay pooled `KEEPALIVE_EXPIRY` seconds, not HTTPX's 5."""
  limits = HttpClient().limits
  assert limits.keepalive_expiry == KEEPALIVE_EXPIRY > 5
  assert limits.max_keepalive_connections == httpx.Limits().max_keepalive_connections


@pytest.mark.parametrize('name', ['HTTP_PROXY', 'HTTPS_PROXY'])
def test_no_keepalive_behind_an_environment_proxy(monkeypatch, name):
  """Behind an environment proxy, idle connections are not kept."""
  monkeypatch.setenv(name, 'http://proxy.invalid:8080')
  assert HttpClient().limits.max_keepalive_connections == 0


def test_explicit_limits_win():
  """Explicit limits configure the pool as given."""
  limits = httpx.Limits(keepalive_expiry=10)
  assert HttpClient(limits=limits).limits is limits


@pytest.mark.asyncio
async def test_idle_connection_is_reused(monkeypatch):
  """A request after an idle pause longer than HTTPX's 5 s reuses the pooled connection."""
  async with Server() as server, HttpClient() as http:
    await http.request('GET', server.url)
    advance_pool_clock(monkeypatch, KEEPALIVE_EXPIRY - 1)
    assert (await http.request('GET', server.url)).text == 'ok'
    assert server.connections == 1


@pytest.mark.asyncio
async def test_expired_connection_is_replaced(monkeypatch):
  """Past `KEEPALIVE_EXPIRY`, the next request opens a new connection."""
  async with Server() as server, HttpClient() as http:
    await http.request('GET', server.url)
    advance_pool_clock(monkeypatch, KEEPALIVE_EXPIRY + 1)
    assert (await http.request('GET', server.url)).text == 'ok'
    assert server.connections == 2


@pytest.mark.asyncio
async def test_server_closed_idle_connection_is_not_a_failed_request():
  """A pooled connection the server closed while idle is discarded, not used: the next
  request succeeds on a new connection."""
  async with Server(idle_close=0.05) as server, HttpClient() as http:
    await http.request('GET', server.url)
    await asyncio.sleep(0.3)
    assert (await http.request('GET', server.url)).text == 'ok'
    assert server.connections == 2
