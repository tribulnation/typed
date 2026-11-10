"""HTTP transports: the Trading API (authenticated per call) and the public backends.

The Trading API verifies an agent signature over the request path (query string
included) and `keccak256` of the body bytes, exactly as received. The transport therefore
builds the final URL and body once, signs the URL's raw path and those bytes, and sends
the same URL and bytes: nothing re-encodes either after signing.
"""

from typing_extensions import Any, Literal, Mapping, TypeVar
from dataclasses import dataclass, field

import httpx

from typed_core.http import HttpClient
from typed_core.validation import validator

from .. import envelope
from ..auth import AgentSigner
from ..endpoint import public
from ..endpoint.public import PublicClient
from ..endpoint.trading import AuthMode, Method, TradingClient
from ..endpoint.wire import encode_query, json_body
from ..exc import AuthError, LogicError

T = TypeVar('T')

JSON_HEADERS = {'Accept': 'application/json'}


def build_url(
  *, base_url: str, path: str, query: Mapping[str, Any] | None
) -> httpx.URL:
  """The final request URL. A `path` of `/` addresses `base_url` itself: the Trading API
  serves its chain root without a trailing slash (`/v1/arbitrum`, not `/v1/arbitrum/`)."""
  url = base_url if path == '/' else base_url + path
  qs = encode_query(query or {})
  return httpx.URL(f'{url}?{qs}' if qs else url)


def should_validate(default: bool, validate: bool | None) -> bool:
  """Per-call override of a transport's `validate` default."""
  return default if validate is None else validate


@dataclass(kw_only=True)
class TradingHttpClient(TradingClient):
  """Trading API HTTP client for one chain: owns its URLs, its credentials, signing and
  validation."""

  base_url: str
  """Chain root, e.g. `https://api.gains.trade/v1/arbitrum`; chain-scoped paths are relative to it."""
  host_url: str
  """API host, e.g. `https://api.gains.trade`, for the operations outside the chain root."""
  http: HttpClient = field(default_factory=HttpClient)
  signer: AgentSigner | None = None
  """Signs `trade` calls, and `read` calls when there is no API key."""
  api_key: str | None = field(default=None, repr=False)
  """Authorizes `read` calls on its own."""
  validate: bool = True

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def auth_headers(
    self, auth: AuthMode, *, operation: str, method: str, url: httpx.URL, body: bytes
  ) -> dict[str, str]:
    """The authentication headers of one call: the API key for a `read` when the client
    has one, else the agent signature over `url`'s raw path and `body`.

    Raises:
      AuthError: The client has no credential this call accepts. Raised before anything
        is sent.
    """
    if auth == 'read' and self.api_key is not None:
      return {'X-Gains-Api-Key': self.api_key}
    if self.signer is None:
      if auth == 'read':
        raise AuthError(
          'This call needs an API key or an agent key: build the client with `api_key` '
          'or `agent` (not `public=True`).'
        )
      raise AuthError(
        'This call needs an agent key (a read-only API key cannot trade): build the '
        'client with `agent`.'
      )
    signed = self.signer.sign(
      operation=operation, method=method, path=url.raw_path.decode('ascii'), body=body
    )
    return signed.headers()

  async def request(
    self,
    method: Method,
    path: str,
    *,
    query: Mapping[str, Any] | None = None,
    body: Mapping[str, Any] | None = None,
    auth: AuthMode | None = None,
    operation: str | None = None,
    root: Literal['chain', 'host'] = 'chain',
    unwrap: str | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request; see `TradingClient.request`.

    Raises:
      AuthError: The call needs a credential the client lacks, or the venue rejected it.
      LogicError: `auth` is set without `operation`.
    """
    url = build_url(
      base_url=self.host_url if root == 'host' else self.base_url,
      path=path,
      query=query,
    )
    content = None if body is None else json_body(body)
    headers = dict(JSON_HEADERS)
    if content is not None:
      headers['Content-Type'] = 'application/json'
    if auth is not None:
      if operation is None:
        raise LogicError('An authenticated call must name its `operation`.')
      headers |= self.auth_headers(
        auth, operation=operation, method=method, url=url, body=content or b''
      )
    response = await self.http.request(
      method, str(url), content=content, headers=headers
    )
    payload = envelope.unwrap(envelope.trading_result(response), unwrap)
    if validator is not None and should_validate(self.validate, validate):
      return validator.python(payload)
    return payload


@dataclass(kw_only=True)
class PublicHttpClient(PublicClient):
  """HTTP client for one public backend host: no credentials, bare-JSON envelope."""

  base_url: str
  """Host root, e.g. `https://backend-arbitrum.gains.trade`."""
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    method: public.Method,
    path: str,
    *,
    query: Mapping[str, Any] | None = None,
    body: Mapping[str, Any] | None = None,
    unwrap: str | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send one request; see `PublicClient.request`."""
    url = build_url(base_url=self.base_url, path=path, query=query)
    content = None if body is None else json_body(body)
    headers = dict(JSON_HEADERS)
    if content is not None:
      headers['Content-Type'] = 'application/json'
    response = await self.http.request(
      method, str(url), content=content, headers=headers
    )
    payload = envelope.unwrap(envelope.public_result(response), unwrap)
    if validator is not None and should_validate(self.validate, validate):
      return validator.python(payload)
    return payload
