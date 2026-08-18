"""HTTP transport for `info` requests."""

from typing_extensions import Any, Mapping
from dataclasses import dataclass, field

from typed_core.exceptions import ApiError
from typed_core.http import HttpClient

from hyperliquid.core.endpoint.rpc import RpcClient


@dataclass(kw_only=True)
class InfoHttpClient(RpcClient):
  """HTTP transport for Hyperliquid info requests."""

  base_url: str
  http: HttpClient = field(default_factory=HttpClient)

  @property
  def url(self) -> str:
    return f'{self.base_url.rstrip("/")}/info'

  async def request(self, payload: Mapping[str, Any]) -> Any:
    r = await self.http.request('POST', self.url, json=payload)
    if r.status_code != 200:
      raise ApiError(r.status_code, r.text)
    return r.json()

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)
