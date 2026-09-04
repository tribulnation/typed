"""HTTP transport for Coinbase Exchange (formerly Pro/GDAX)'s REST API.

Verified live (2026-08-27): `GET /time` and `GET /products` succeed unauthenticated;
`GET /accounts` and `GET /orders` with no credentials both return `401
{"message":"Unauthorized."}`; a nonexistent product/currency returns `404
{"message":"NotFound"}` — matching the official OpenAPI spec's `apiErrorResponse`/
`apiUnauthorizedResponse` shape, `{"message": string}` with no structured error code. HTTP
status is the sole failure discriminator, exactly like `typed_coinbase.core.transport.http`'s
App transport, so `raise_http_status` is reused from there rather than redefined — it is a
pure `httpx.Response -> typed_core exception` mapping with no App-specific (JWT/`Credentials`)
dependency, i.e. exactly the kind of generic helper this client's `spec/core.md` calls out as
worth sharing across surfaces rather than duplicating. Everything else here (base URL,
`Credentials`, signing, the request/authed_request split) is Exchange's own — a structurally
distinct sub-client from App, with its own HMAC scheme and its own host.

No live authenticated call has been made against this transport: no Exchange credentials
are provisioned (`client.toml`'s `[secrets]` only lists the variable names, and there is no
`[policy]` approving their use yet — see `spec/core.md`). `authed_request` is written to the
documented signing scheme and exercised only by unit tests with a mock server, not a real
account.
"""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass, field
from urllib.parse import urlencode
import json as json_lib
import httpx

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.validation import validator

from typed_coinbase.core.endpoint.rpc import RpcClient
from typed_coinbase.core.transport.http import raise_http_status
from ..auth import Credentials, auth_headers

T = TypeVar('T')

BASE_URL = 'https://api.exchange.coinbase.com'
"""Production host. The sandbox (`api-public.sandbox.exchange.coinbase.com`) is a distinct,
separately-keyed environment — out of scope for now, see `spec/core.md`."""


def unwrap(response: httpx.Response) -> Any:
  """Return the decoded JSON body, raising on a non-2xx HTTP status.

  Raises:
    ApiError: The HTTP status was unsuccessful.
  """
  if not response.is_success:
    raise_http_status(response)
  return response.json()


def _path_with_query(path: str, params: Mapping[str, Any] | None) -> str:
  """Build the exact request-path-plus-query string both signed and sent for a private
  request. Built here, once, rather than left to `httpx`'s own query encoding, so the
  string this signs and the string actually placed on the wire can never drift apart.
  """
  if not params:
    return path
  query = urlencode({k: v for k, v in params.items() if v is not None}, doseq=True)
  return f'{path}?{query}' if query else path


@dataclass(kw_only=True)
class ExchangeHttpRpcClient(RpcClient):
  """HTTP RPC client for Coinbase Exchange, owning connection, authentication and validation."""

  base_url: str = BASE_URL
  http: HttpClient = field(default_factory=HttpClient)
  credentials: Credentials | None = None
  """`None` means unauthenticated: only public endpoints can be called."""
  validate: bool = True

  async def __aenter__(self):
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
    json: Any | None = None,
    content: bytes | None = None,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned request to `base_url + path`.

    Args:
      content: A pre-serialized JSON body (`typed_core.validation.validator.dump`'s own
        output) -- bypasses `httpx`'s own JSON encoding, needed for a body carrying a
        `Decimal`/`datetime` field it can't encode itself.
    """
    response = await self.http.request(
      method, self.base_url + path, json=json, content=content, params=params
    )
    return self.result(response, validator=validator, validate=validate)

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    json: Any | None = None,
    content: bytes | None = None,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request, HMAC-bound to this exact method, path, query, and body.

    Args:
      content: A pre-serialized JSON body (`typed_core.validation.validator.dump`'s own
        output) -- bypasses `httpx`'s own JSON encoding, needed for a body carrying a
        `Decimal`/`datetime` field it can't encode itself. Signed verbatim, the same way
        a `json`-encoded body is.

    Raises:
      AuthError: This client was built with no credentials (`exchange_public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `exchange_public=True`.')
    full_path = _path_with_query(path, params)
    if content is not None:
      body = content.decode()
    elif json is not None:
      body = json_lib.dumps(json, separators=(',', ':'))
    else:
      body = ''
    headers = auth_headers(self.credentials, method=method.upper(), path=full_path, body=body)
    if json is not None or content is not None:
      headers['Content-Type'] = 'application/json'
    response = await self.http.request(
      method,
      self.base_url + full_path,
      content=body.encode() if (json is not None or content is not None) else None,
      headers=headers,
    )
    return self.result(response, validator=validator, validate=validate)

  def result(
    self,
    response: httpx.Response,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
  ) -> T:
    """Unwrap the envelope and map errors, then validate — what every generated endpoint
    method calls to turn an `httpx.Response` into a typed result.
    """
    payload = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload
