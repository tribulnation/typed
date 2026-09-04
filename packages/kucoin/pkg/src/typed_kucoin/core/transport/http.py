"""HTTP transport for the KuCoin REST API: connection, authentication and validation
shared by every Classic product — they share one envelope and one signing scheme, and
differ only in which of the three base URLs below an `HttpRpcClient` is rooted at. See
`spec/core.md` §Surfaces / §Transport / §Envelope / §Authentication.
"""

from typing_extensions import Any, Mapping, Self, TypeVar
from dataclasses import dataclass, field
from urllib.parse import urlencode
import json as _json
import time
import httpx

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.validation import validator

from ..endpoint.rpc import RpcClient
from ..auth import Credentials, auth_headers
from ..envelope import unwrap

T = TypeVar('T')

DEFAULT_API_URL = 'https://api.kucoin.com'
"""Base URL for the Account, Spot, Margin, Earn, VIP Lending and Convert products."""

FUTURES_API_URL = 'https://api-futures.kucoin.com'
"""Base URL for the Futures and Copy Trading (futures-only) products."""

BROKER_API_URL = 'https://api-broker.kucoin.com'
"""Base URL for the Broker product."""


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """HTTP RPC client for one KuCoin base URL, owning connection, authentication and
  validation. Every Classic product shares this one implementation, each rooted at
  whichever of the three base URLs above its product needs — see `spec/core.md`
  §Surfaces.
  """

  base_url: str = DEFAULT_API_URL
  http: HttpClient = field(default_factory=HttpClient)
  credentials: Credentials | None = None
  """`None` means unauthenticated: only public endpoints can be called."""
  validate: bool = True

  async def __aenter__(self) -> Self:
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    content: bytes | None = None,
    headers: Mapping[str, str] | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned request to `base_url + path`."""
    response = await self.http.request(
      method,
      self.base_url + path,
      json=json,
      content=content,
      params=params,
      headers=headers,
    )
    return self.result(response, validator, validate=validate)

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    content: bytes | None = None,
    headers: Mapping[str, str] | None = None,
    validator: 'validator[T] | None' = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request.

    Builds the exact query string and compact JSON body by hand, then signs that
    string — handing `params`/`json` to `httpx` and letting it encode them
    independently could produce wire bytes that don't match what was signed, and KuCoin
    rejects the signature if they don't. When the caller already has the exact wire bytes
    (`content`, from a generated method's `validator(Type).dump(body)`), those bytes are
    decoded to build the signed string and then sent unchanged — never re-encoded — so the
    signed string and the sent bytes stay identical by construction.

    Args:
      method: HTTP method, for example `GET`.
      path: Path relative to the base URL, for example `/api/v2/user-info`.
      params: Query string parameters.
      json: JSON request body, for a caller with no pre-serialized wire bytes.
      content: Pre-serialized JSON request body bytes, signed and sent verbatim. Takes
        precedence over `json` when both are given.
      headers: Extra headers to send alongside the signed `KC-API-*` ones — every
        endpoint but `broker.rebate_download_v3` (its own `x-tenant`) needs none.
      validator: Adapter to validate the unwrapped result against, if any.
      validate: Per-call override of the client-level `validate` default.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError(
        f'{path} requires credentials; build the client with '
        '`KuCoin.new(api_key=..., api_secret=..., api_passphrase=...)`.'
      )
    query = urlencode(params, safe=',') if params else ''
    if content is not None:
      body = content.decode('utf-8')
    else:
      body = _dumps(json) if json is not None else ''
    endpoint = path + (f'?{query}' if query else '')
    timestamp = str(int(time.time() * 1000))
    signed_headers = auth_headers(
      self.credentials,
      timestamp=timestamp,
      method=method.upper(),
      endpoint=endpoint,
      body=body,
    )
    if body:
      signed_headers['Content-Type'] = 'application/json'
    if headers:
      signed_headers.update(headers)
    response = await self.http.request(
      method,
      self.base_url + endpoint,
      content=content if content is not None else (body or None),
      headers=signed_headers,
    )
    return self.result(response, validator, validate=validate)

  def result(
    self,
    response: httpx.Response,
    validator: 'validator[T] | None' = None,
    *,
    validate: bool | None = None,
  ) -> T:
    """Unwrap the envelope and map errors, then validate — what `request`/
    `authed_request` funnel every response through to produce a typed result.
    """
    payload = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload


def _dumps(json: Any) -> str:
  return _json.dumps(json, separators=(',', ':'))
