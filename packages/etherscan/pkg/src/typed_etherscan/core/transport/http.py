"""HTTP transport: base URL, `apikey`-query-param auth, envelope unwrapping and
response validation."""

from typing_extensions import Any, Mapping, TypeVar
from dataclasses import dataclass, field
import httpx

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient
from typed_core.util import RateLimit
from typed_core.validation import validator

from ..endpoint.rpc import RpcClient
from ..envelope import unwrap

T = TypeVar('T')

ETHERSCAN_API_URL = 'https://api.etherscan.io'
"""Host shared by both of Etherscan's V2 paths: `/v2/api` (module/action dispatch) and
`/v2/chainlist` (the one endpoint outside that dispatch)."""


@dataclass(kw_only=True)
class HttpRpcClient(RpcClient):
  """HTTP client for the Etherscan V2 API, owning connection, auth and validation."""

  base_url: str = ETHERSCAN_API_URL
  http: HttpClient = field(default_factory=HttpClient)
  api_key: str | None = None
  """`None` means unauthenticated: only an endpoint declaring no `auth`
  (`usage.chain_list`) can be called."""
  rate_limit: RateLimit | None = None
  """Client-side cap on calls per second, cooperative rather than reactive -- Etherscan's
  free tier enforces a strict one."""
  validate: bool = True

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)

  def should_validate(self, validate: bool | None = None) -> bool:
    """Per-call override of the client-level `validate` default."""
    return self.validate if validate is None else validate

  async def _send(
    self, method: str, path: str, *,
    params: Mapping[str, Any] | None, data: Mapping[str, Any] | None,
  ) -> httpx.Response:
    url = self.base_url + path
    if self.rate_limit is None:
      return await self.http.request(method, url, params=params, data=data)
    async with self.rate_limit:
      return await self.http.request(method, url, params=params, data=data)

  async def request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    data: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send an unauthenticated request. Only `usage.chain_list` uses this."""
    response = await self._send(method, path, params=params, data=data)
    return self.result(response, validator=validator, validate=validate)

  async def authed_request(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    data: Mapping[str, Any] | None = None,
    validator: validator[T] | None = None,
    validate: bool | None = None,
  ) -> T:
    """Send a request with the API key attached as the `apikey` query parameter.

    Raises:
      AuthError: This client was built with no API key (`public=True` upstream).
    """
    if self.api_key is None:
      raise AuthError('No credentials: this client was built with `public=True`.')
    params = {'apikey': self.api_key, **(params or {})}
    response = await self._send(method, path, params=params, data=data)
    return self.result(response, validator=validator, validate=validate)

  def result(
    self,
    response: httpx.Response,
    validator: validator[T] | None = None,
    *,
    validate: bool | None = None,
  ) -> T:
    """Unwrap the envelope, then validate -- what every generated endpoint method calls
    to turn an `httpx.Response` into a typed result."""
    payload = unwrap(response)
    if validator is not None and self.should_validate(validate):
      return validator.python(payload)
    return payload
