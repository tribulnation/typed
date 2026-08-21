"""HTTP transport: the shared REST client behind both the Classic and Uta surfaces.

One `HttpRpcClient` instance backs both `/api/v2/...` (Classic) and `/api/v3/...` (Uta)
paths — same host, same envelope, same signing scheme — so `Classic`/`Uta` each hold a
reference to the *same* client rather than owning one each; see `spec/core.md` Surfaces.
"""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass, field
from urllib.parse import urlencode
import json as _json

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.validation import validator
import httpx

from ..endpoint.rpc import RpcClient
from ..auth import Credentials, auth_headers
from ..envelope import unwrap
from ..types import timestamp_millis

T = TypeVar('T')

BITGET_API_URL = 'https://api.bitget.com'


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """HTTP RPC client, owning connection, authentication and validation."""

  base_url: str = BITGET_API_URL
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
    sorted_params = dict(sorted(params.items())) if params else None
    response = await self.http.request(
      method, self.base_url + path, json=json, params=sorted_params
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
    """Sign and send one request. Query params are sorted alphabetically by key, and that
    exact sorted order is both signed and sent, so what's signed is what goes over the wire.

    Raises:
      AuthError: This client was built with no credentials (`public=True` upstream).
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    sorted_params = dict(sorted(params.items())) if params else {}
    query = urlencode(sorted_params)
    signed_path = f'{path}?{query}' if query else path
    body = None if json is None else _json.dumps(json, separators=(',', ':'))
    headers = auth_headers(
      self.credentials,
      timestamp=str(timestamp_millis.now()),
      method=method,
      path=signed_path,
      body=body,
    )
    response = await self.http.request(
      method, self.base_url + path, content=body, params=sorted_params, headers=headers
    )
    return self.result(response, validator=validator, validate=validate)

  def result(
    self,
    response: httpx.Response,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
  ) -> T:
    """Unwrap the envelope and map errors, then validate — what every endpoint method calls
    to turn an `httpx.Response` into a typed result.
    """
    payload = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload
