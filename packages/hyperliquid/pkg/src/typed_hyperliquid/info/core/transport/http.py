"""HTTP transport for `info` requests."""

from typing_extensions import Any, Mapping
from dataclasses import dataclass, field

from typed_core.exceptions import ApiError, RateLimited
from typed_core.http import HttpClient

from typed_hyperliquid.core.endpoint.rpc import RpcClient


@dataclass(kw_only=True)
class InfoHttpClient(RpcClient):
  """HTTP transport for Hyperliquid info requests."""

  base_url: str
  http: HttpClient = field(default_factory=HttpClient)

  @property
  def url(self) -> str:
    return f'{self.base_url.rstrip("/")}/info'

  async def request(self, payload: Mapping[str, Any]) -> Any:
    """Send one `info` request and return its decoded response.

    Raises:
      RateLimited: HTTP status `429`, regardless of the response body's format.
      ApiError: Any other non-`200` status.

    References:
      - [Rate Limits and User Limits](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/rate-limits-and-user-limits)
    """
    r = await self.http.request('POST', self.url, json=payload)
    if r.status_code == 429:
      raise RateLimited(r.status_code, r.text)
    if r.status_code != 200:
      raise ApiError(r.status_code, r.text)
    return r.json()

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)
