"""Bybit v5 REST transport and the resolved `default` core (design §5/§6): design §2's
single `request()` verb, deciding public-vs-signed purely from `meta['signed']`, and
query-string-vs-JSON-body purely from the wire HTTP method -- every real Bybit v5 REST
endpoint sends a `GET` as a query string and anything else as a JSON body, confirmed
against the fleet of live-captured examples; the small number of unverified,
documentation-only `web3.trade.*` endpoints whose original spec happened to route a
`POST`'s fields through `parameters[]` (query string) rather than `requestBody` never had
that placement live-confirmed either way, so this migration standardizes them onto the
same by-method rule the rest of the client already uses live, rather than preserving an
unconfirmed inconsistency.
"""

from typing_extensions import Any, Literal, Mapping, NotRequired, Self, TypedDict, TypeVar, cast
from dataclasses import dataclass, field
from types import UnionType
import json as _json
import time
from urllib.parse import urlencode
import httpx

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.validation import validator

from .auth import Credentials, rest_headers
from .envelope import unwrap

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


@dataclass(kw_only=True, frozen=True)
class HttpTransport:
  """Shared low-level REST sender: base URL, raw HTTP client, credentials, and the
  client-level validation default -- every field every Bybit v5 REST endpoint needs
  regardless of which product it belongs to. Forwarded, unchanged, to every generated
  `RpcEndpoint` in the `http`/`default` subtree (design §5c's `children` mapping default:
  `{child_class}(client=self.client)`).
  """

  base_url: str = BYBIT_API_URL
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True
  credentials: Credentials | None = None
  """API key and secret, shared by every authenticated endpoint on this client. `None`
  means unauthenticated: only public endpoints can be called."""

  def should_validate(self, validate: bool | None = None) -> bool:
    """Resolve a per-call validation override against the client default."""
    return self.validate if validate is None else validate

  async def __aenter__(self) -> Self:
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self, method: str, path: str, *, params: dict[str, Any] | None = None,
  ) -> httpx.Response:
    """Send an unsigned request against this client's base URL.

    Args:
      method: HTTP method, for example `GET`.
      path: Path relative to the base URL, for example `/v5/market/tickers`.
      params: Fields to send -- a query string for `GET`, a JSON body otherwise.
    """
    if method == 'GET':
      return await self.http.request(method, self.base_url + path, params=params)
    return await self.http.request(method, self.base_url + path, json=params)

  async def authed_request(
    self, method: str, path: str, *, params: dict[str, Any] | None = None,
  ) -> httpx.Response:
    """Send a signed request against this client's base URL.

    Builds the exact query string (`GET`) or compact JSON body (anything else) by hand
    and signs that string, rather than handing `params`/`json` to `httpx` and letting it
    encode them independently — the signed string and the wire bytes must be byte for
    byte identical or Bybit rejects the signature.

    Args:
      method: HTTP method, for example `POST`.
      path: Path relative to the base URL, for example `/v5/account/wallet-balance`.
      params: Fields to send -- a query string for `GET`, a JSON body otherwise.

    Raises:
      AuthError: The client holds no credentials.
    """
    if self.credentials is None:
      raise AuthError(
        f'{path} requires credentials; build the client with '
        '`Bybit.new(api_key=..., api_secret=...)`.'
      )
    query = urlencode(params) if method == 'GET' and params else ''
    body = (
      _json.dumps(params, separators=(',', ':'))
      if method != 'GET' and params is not None
      else ''
    )
    timestamp = str(int(time.time() * 1000))
    headers = rest_headers(self.credentials, timestamp=timestamp, payload=query or body)
    url = self.base_url + path + (f'?{query}' if query else '')
    if body:
      headers['Content-Type'] = 'application/json'
    return await self.http.request(method, url, content=body or None, headers=headers)


class Meta(TypedDict):
  """`default`'s own `meta` shape (`codegen/config.toml` `[cores.default].meta`): whether this
  call needs HMAC-SHA256 signing. Hand-written to match that declared JSON Schema --
  never code-generated (design §2/§6, the same precedent this repo already uses for a
  spec-declared timestamp `format`; S27)."""

  signed: NotRequired[bool]
  """Whether this call needs HMAC-SHA256 signing (absent/`False` for a public endpoint)."""


@dataclass(kw_only=True, frozen=True)
class RpcEndpoint:
  """Base class for every Bybit v5 REST endpoint -- the resolved `default` core for the
  whole REST subtree (`codegen/config.toml`)."""

  client: HttpTransport

  async def __aenter__(self) -> Self:
    await self.client.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.client.__aexit__(exc_type, exc_value, traceback)

  async def request(
    self,
    request: Any = None,
    *,
    method: str,
    path: str,
    meta: Meta,
    validate: bool | None = None,
    request_type: type[Any] | UnionType | None = None,
    response_type: type[T] | UnionType | None = None,
  ) -> T:
    """Perform one REST call (design §2's single verb): serialize `request` through
    `request_type`'s validator (ADR 0020/S28) into a plain, wire-ready dict, send it as a
    query string (`GET`) or JSON body (anything else) -- signed when `meta['signed']`,
    unsigned otherwise -- and validate the reply's unwrapped `result` through
    `response_type`'s validator.

    Args:
      request: The generated `Request` value (a `TypedDict` instance, or `None` for a
        parameterless operation).
      method: Wire HTTP verb.
      path: Wire path, e.g. `/v5/account/wallet-balance`.
      meta: This call's own quirks -- whether it needs HMAC-SHA256 signing.
      validate: Per-call override of response validation.
      request_type: The generated request type, used to serialize `request`.
      response_type: The generated response type, used to validate the reply.
    """
    values = (
      _json.loads(validator(cast(type, request_type)).dump(request))
      if request_type is not None and request is not None
      else None
    )
    response_validator = (
      validator(cast(type, response_type)) if response_type is not None else None
    )
    call = self.client.authed_request if meta.get('signed', False) else self.client.request
    r = await call(method, path, params=values)
    payload = unwrap(r)
    if response_validator is not None and self.client.should_validate(validate):
      return response_validator.python(payload)
    return payload
