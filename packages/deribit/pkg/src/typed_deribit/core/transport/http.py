"""HTTP transport: two `RpcClient` implementations, one per HTTP auth scheme Deribit
documents (see `spec/core.md`'s Authentication section) —

- `OAuthHttpRpcClient` (default): `public/auth` token exchange, `Authorization: Bearer <token>`.
- `HmacHttpRpcClient` (opt-in): per-request `client_signature` HMAC signing, no token
  exchange.

Both share `DeribitHttpClient` for the unauthenticated path and envelope/validation
handling; they differ only in `authed_request`.

Every request is `POST {base_url}/{method}` carrying the standard JSON-RPC 2.0 envelope
(`{jsonrpc, id, method, params}`) as a JSON body — confirmed live against
`test.deribit.com` that `method` must be present in the body even though it's redundant
with the URL path (a body carrying only `params` is rejected, `{code: 11050, message:
'bad_request'}`); `jsonrpc`/`id` are accepted but not required, included anyway to match
the shape `spec/discovery.md` documents and what the WebSocket transport already sends.
This replaced an earlier `GET` + query-string design, dropped because Deribit's query
string cannot express an array-of-objects param (`create_combo`'s `trades`, `mass_quote`'s
`quotes`, ... — see `spec/core.md`'s Transport section for the confirmed-live evidence).
"""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass, field
import json

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.validation import validator
import httpx

from ..auth import AuthResult, Credentials, TokenCache, hmac_auth_header
from ..envelope import unwrap

T = TypeVar('T')

REQUEST_ID = 0
"""Every HTTP request/response pairs synchronously (unlike WebSocket, where many
in-flight calls share one connection and need distinct ids to correlate replies) — so
one constant id is enough to satisfy the JSON-RPC envelope shape without meaning
anything more here."""


def build_body(method: str, params: Mapping[str, Any] | None) -> str:
  """Serialize one JSON-RPC request envelope, exactly as sent (and, for
  `HmacHttpRpcClient`, exactly as signed)."""
  return json.dumps(
    {'jsonrpc': '2.0', 'id': REQUEST_ID, 'method': method, 'params': params or {}}
  )


DERIBIT_HTTP_URL = 'https://www.deribit.com/api/v2'
DERIBIT_TEST_HTTP_URL = 'https://test.deribit.com/api/v2'


def resolve_http_base_url(testnet: bool) -> str:
  """Return Deribit's HTTP JSON-RPC base URL for mainnet or testnet."""
  return DERIBIT_TEST_HTTP_URL if testnet else DERIBIT_HTTP_URL


@dataclass(kw_only=True)
class DeribitHttpClient:
  """Shared connection, envelope-unwrapping and validation for both HTTP auth schemes.

  Not itself a complete `RpcClient` — it has no `authed_request`, only the two concrete
  subclasses below do.
  """

  base_url: str = DERIBIT_HTTP_URL
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of this client's `validate` default."""
    return self.validate if validate is None else validate

  async def request(
    self,
    method: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unauthenticated `POST` request to `{base_url}/{method}`."""
    response = await self.http.request(
      'POST',
      f'{self.base_url}/{method}',
      content=build_body(method, params),
      headers={'Content-Type': 'application/json'},
    )
    return self.result(response, validator, validate=validate)

  def result(
    self,
    response: httpx.Response,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
  ) -> T:
    """Unwrap the JSON-RPC envelope, then validate — what every endpoint method calls to
    turn an `httpx.Response` into a typed result."""
    payload = unwrap(response.text)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload


@dataclass(kw_only=True)
class OAuthHttpRpcClient(DeribitHttpClient):
  """Default HTTP transport: `public/auth` token exchange, Bearer header per request."""

  credentials: Credentials | None = None
  """`None` means unauthenticated: only public methods can be called."""
  tokens: TokenCache | None = field(default=None, init=False, repr=False)

  def __post_init__(self):
    if self.credentials is not None:
      self.tokens = TokenCache(self.credentials)

  async def authenticate(self, credentials: Credentials) -> AuthResult:
    """Exchange `client_id`/`client_secret` for an access token via `public/auth`."""
    return await self.request(
      'public/auth',
      params={
        'grant_type': 'client_credentials',
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
      },
    )

  async def authed_request(
    self,
    method: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send a Bearer-authenticated request, lazily exchanging and caching a token.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None or self.tokens is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    token = await self.tokens.get(self.authenticate)
    response = await self.http.request(
      'POST',
      f'{self.base_url}/{method}',
      content=build_body(method, params),
      headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
      },
    )
    return self.result(response, validator, validate=validate)


@dataclass(kw_only=True)
class HmacHttpRpcClient(DeribitHttpClient):
  """Opt-in HTTP transport: per-request `client_signature` HMAC signing, no token
  exchange. Confirmed against a live signed call, see `core.auth`'s module docstring.
  """

  credentials: Credentials | None = None
  """`None` means unauthenticated: only public methods can be called."""

  async def authed_request(
    self,
    method: str,
    *,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request. Signs the exact body that gets sent, not a
    reconstruction of it — build the body first, then sign, then send.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    body = build_body(method, params)
    uri = f'/api/v2/{method}'
    header = hmac_auth_header(self.credentials, method='POST', uri=uri, body=body)
    response = await self.http.request(
      'POST',
      f'{self.base_url}/{method}',
      content=body,
      headers={'Content-Type': 'application/json', 'Authorization': header},
    )
    return self.result(response, validator, validate=validate)
