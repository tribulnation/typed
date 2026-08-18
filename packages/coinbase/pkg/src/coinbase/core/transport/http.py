"""HTTP transport for both the v2 (Coinbase App) and v3 (Advanced Trade) REST families.

Verified live: v2 and v3 sit on one host, authenticated by one CDP API Key, and both
signal failure the same way — a non-2xx HTTP status, body `{"error", "message", ...}` —
so one `unwrap` covers both; HTTP status is the only failure discriminator, so it is
folded in here rather than split into its own `envelope.py` (see `docs/spec/authoring.md`
rule 5). v2 wraps successful responses as `{"data": ..., "pagination": {...}}` and v3
returns the resource flat, sometimes with pagination fields (`has_next`/`cursor`) beside
it — neither is unwrapped, since v2's cursor fields live in `pagination`, outside `data`.
"""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass, field
import httpx

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited
from typed_core.http import HttpClient
from typed_core.validation import validator

from ..endpoint.rpc import RpcClient
from ..auth import Credentials, auth_headers

T = TypeVar('T')

BASE_URL = 'https://api.coinbase.com'
HOST = 'api.coinbase.com'
"""Bound into every signed request's JWT `uri` claim — must match `BASE_URL`'s host."""


def raise_http_status(response: httpx.Response):
  """Raise the `typed_core` exception matching a non-2xx HTTP status.

  Args:
    response: The unsuccessful HTTP response.

  Raises:
    AuthError: Status `401` or `403`.
    RateLimited: Status `429`.
    BadRequest: Any other `4xx` status.
    ApiError: Any other unsuccessful status.
  """
  try:
    payload: Any = response.json()
  except ValueError:
    payload = response.text
  status = response.status_code
  if status in (401, 403):
    raise AuthError(status, payload)
  if status == 429:
    raise RateLimited(status, payload)
  if 400 <= status < 500:
    raise BadRequest(status, payload)
  raise ApiError(status, payload)


def unwrap(response: httpx.Response) -> Any:
  """Return the decoded JSON body, raising on a non-2xx HTTP status.

  Raises:
    ApiError: The HTTP status was unsuccessful.
  """
  if not response.is_success:
    raise_http_status(response)
  return response.json()


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """HTTP RPC client, owning connection, authentication and validation."""

  base_url: str = BASE_URL
  host: str = HOST
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
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned request to `base_url + path`."""
    response = await self.http.request(
      method, self.base_url + path, json=json, params=params
    )
    return self.result(response, validator=validator, validate=validate)

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    json: Any | None = None,
    params: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request, JWT-bound to this exact method and path.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    headers = auth_headers(self.credentials, method=method, host=self.host, path=path)
    response = await self.http.request(
      method, self.base_url + path, json=json, params=params, headers=headers
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
