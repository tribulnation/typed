"""Spot HTTP transport: connection, signing and envelope handling for the RPC surface."""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass, field

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.times import EpochConverter
from typed_core.validation import validator
import httpx

from ....core.auth import Credentials
from ....core.endpoint.rpc import RpcClient
from ..auth import signed_query
from ..envelope import unwrap

T = TypeVar('T')

MEXC_SPOT_API_BASE = 'https://api.mexc.com'

request_time = EpochConverter.milliseconds()
"""Millisecond epoch clock for the `timestamp` signing parameter -- not a wire-response
converter, so it lives beside the transport rather than in a shared `types.py`.
"""


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """Spot HTTP RPC client, owning connection, authentication and validation."""

  base_url: str = MEXC_SPOT_API_BASE
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
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unsigned request to `base_url + path`."""
    response = await self.http.request(
      method, self.base_url + path, params=params, json=json
    )
    return self.result(response, validator=validator, validate=validate)

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Sign and send one request.

    Spot signs the exact query string sent -- every business parameter plus `timestamp`
    -- as one `totalParams` string; the key itself travels in an `X-MEXC-APIKEY` header,
    not in the signed string.

    Raises:
      AuthError: This client was built with no credentials.
    """
    if self.credentials is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    signed_params = {**(params or {}), 'timestamp': request_time.now()}
    query = signed_query(signed_params, secret=self.credentials.api_secret)
    response = await self.http.request(
      method, f'{self.base_url}{path}?{query}',
      json=json, headers={'X-MEXC-APIKEY': self.credentials.api_key},
    )
    return self.result(response, validator=validator, validate=validate)

  def result(
    self,
    response: httpx.Response,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
  ) -> T:
    """Unwrap the envelope and map errors, then validate."""
    payload = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload
