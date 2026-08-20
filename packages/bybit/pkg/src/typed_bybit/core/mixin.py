"""Base endpoint and router for the Bybit v5 REST API."""

from typing_extensions import Any, Literal, Mapping, Self, TypeVar, get_type_hints
from dataclasses import dataclass, field
import json as _json
import time
from urllib.parse import urlencode
import httpx

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient

from .auth import Credentials, rest_headers
from .envelope import unwrap
from .validation import validator

T = TypeVar('T')

Region = Literal['global', 'bytick', 'eu', 'nl', 'tr', 'kz', 'ge', 'ae', 'id', 'jp']
"""One documented Bybit legal entity, keying both its REST and WebSocket domain.

`testnet` is a separate, orthogonal choice (see `resolve_rest_base_url`) rather than a
value of `Region` — only `global` and `jp` are confirmed to document a testnet host, so
folding it into this type would suggest every region has one.

The regional hosts serve different legal entities and therefore **different product
universes** — `'eu'` in particular lists no derivatives at all. See the coverage table
in the client docs before switching.

References:
  - [Bybit v5 base endpoints](https://bybit-exchange.github.io/docs/v5/guide)
"""

BYBIT_DOMAINS: Mapping[Region, str] = {
  'global': 'bybit.com',
  'bytick': 'bytick.com',
  'eu': 'bybit.eu',
  'nl': 'bybit.nl',
  'tr': 'bybit.tr',
  'kz': 'bybit.kz',
  'ge': 'bybitgeorgia.ge',
  'ae': 'bybit.ae',
  'id': 'bybit.id',
  'jp': 'manepa.jp',
}
"""Bare domain of every documented Bybit region, keyed by `Region`.

Both `resolve_rest_base_url` here and `resolve_ws_urls` (`.ws`) build on this same map,
so a region names one domain across both transports even though each prefixes it
differently (`api.`/`api-testnet.` vs `stream.`/`stream-testnet.`, the latter only for
the regions that document a dedicated WebSocket host).
"""

BYBIT_API_URL = 'https://api.bybit.com'
"""Bybit mainnet REST base URL — `region='global'`, `testnet=False`."""


def resolve_rest_base_url(region: Region, *, testnet: bool = False) -> str:
  """Return the REST base URL of a documented Bybit region.

  Every region's REST host follows the same shape — `api` (or `api-testnet`) on that
  region's domain — confirmed live for `global`/`bytick` (`api-testnet.bybit.com`) and
  `jp` (`api-testnet.manepa.jp`). The other seven regions document no testnet host at
  all; `testnet=True` still builds the same-shaped URL for them, without a confirmation
  it resolves to anything live.

  Args:
    region: Legal entity to target.
    testnet: Target that region's testnet host instead of mainnet.

  Raises:
    ValueError: `region` is not one of `BYBIT_DOMAINS`.

  References:
    - [Bybit v5 base endpoints](https://bybit-exchange.github.io/docs/v5/guide)
  """
  domain = BYBIT_DOMAINS.get(region)
  if domain is None:
    known = ', '.join(repr(k) for k in BYBIT_DOMAINS)
    raise ValueError(f'Unknown Bybit region {region!r}. Expected one of {known}.')
  subdomain = 'api-testnet' if testnet else 'api'
  return f'https://{subdomain}.{domain}'


@dataclass(kw_only=True)
class Endpoint:
  """Shared transport, validation defaults and envelope handling for Bybit endpoints."""

  base_url: str = BYBIT_API_URL
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True
  credentials: Credentials | None = None
  """API key and secret, shared by every authenticated endpoint on this client. `None`
  means unauthenticated: only public endpoints can be called."""

  @classmethod
  def new(
    cls,
    *,
    credentials: Credentials | None = None,
    base_url: str = BYBIT_API_URL,
    validate: bool = True,
    http: HttpClient | None = None,
  ) -> Self:
    """Create a client from an already-resolved base URL and credentials.

    This is the thin, transport-local constructor: no environment lookup, no
    region/testnet resolution. `Bybit.new` (`bybit.main`) owns that once, for both this
    and `Ws.new` (`bybit.ws`), so the two transports can't resolve "region X, testnet"
    to two different answers. Call this directly to build `Http`/`Market`/etc. in
    isolation — tests, or a base URL that isn't one of Bybit's own regions (a mock
    server, a private gateway) — via `resolve_rest_base_url` yourself first if needed.

    Args:
      credentials: API key and secret; omit for a client restricted to public endpoints.
      base_url: Fully-qualified REST base URL.
      validate: Validate responses by default.
      http: Shared HTTP client override.
    """
    return cls(
      base_url=base_url,
      http=http or HttpClient(),
      validate=validate,
      credentials=credentials,
    )

  def should_validate(self, validate: bool | None = None) -> bool:
    """Resolve a per-call validation override against the client default."""
    return self.validate if validate is None else validate

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: Any | None = None,
  ) -> httpx.Response:
    """Send a raw HTTP request against this client's base URL.

    Args:
      method: HTTP method, for example `GET`.
      path: Path relative to the base URL, for example `/v5/market/tickers`.
      params: Query string parameters.
      json: JSON request body.
    """
    return await self.http.request(
      method, self.base_url + path, params=params, json=json
    )

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: Any | None = None,
  ) -> httpx.Response:
    """Send a signed HTTP request against this client's base URL.

    Builds the exact query string (`GET`) or compact JSON body (`POST`) by hand and
    signs that string, rather than handing `params`/`json` to `httpx` and letting it
    encode them independently — the signed string and the wire bytes must be byte for
    byte identical or Bybit rejects the signature.

    Args:
      method: HTTP method, for example `POST`.
      path: Path relative to the base URL, for example `/v5/account/wallet-balance`.
      params: Query string parameters.
      json: JSON request body.

    Raises:
      AuthError: The client holds no credentials.
    """
    if self.credentials is None:
      raise AuthError(
        f'{path} requires credentials; build the client with '
        '`Bybit.new(api_key=..., api_secret=...)`.'
      )
    query = urlencode(params) if params else ''
    body = _json.dumps(json, separators=(',', ':')) if json is not None else ''
    timestamp = str(int(time.time() * 1000))
    headers = rest_headers(self.credentials, timestamp=timestamp, payload=query or body)
    url = self.base_url + path + (f'?{query}' if query else '')
    if body:
      headers['Content-Type'] = 'application/json'
    return await self.http.request(method, url, content=body or None, headers=headers)

  def result(
    self,
    response: httpx.Response,
    adapter: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Unwrap a v5 envelope and optionally validate its `result` payload.

    Args:
      response: The HTTP response returned by `request`.
      adapter: Validator for the `result` payload.
      validate: Validation override for this call.

    Raises:
      ApiError: `retCode` was non-zero or the HTTP status was unsuccessful.
      ValidationError: The payload did not match the expected schema.
    """
    payload = unwrap(response)
    if adapter is not None and self.should_validate(validate):
      return adapter.python(payload)
    return payload


@dataclass(kw_only=True)
class Router(Endpoint):
  """Endpoint that instantiates its annotated child endpoints and routers."""

  def __post_init__(self):
    for name, cls in get_type_hints(type(self)).items():
      if isinstance(cls, type) and issubclass(cls, Endpoint):
        setattr(
          self,
          name,
          cls(
            base_url=self.base_url,
            http=self.http,
            validate=self.validate,
            credentials=self.credentials,
          ),
        )


__all__ = [
  'BYBIT_API_URL',
  'BYBIT_DOMAINS',
  'Credentials',
  'Endpoint',
  'HttpClient',
  'Region',
  'Router',
  'resolve_rest_base_url',
]
