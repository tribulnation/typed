"""HTTP transport for `exchange` (wallet-signed) requests."""

from typing_extensions import Any, Mapping
from dataclasses import dataclass, field

from typed_core.exceptions import ApiError
from typed_core.http import HttpClient

from hyperliquid.core.endpoint.rpc import RpcClient
from ..envelope import response_adapter


@dataclass(kw_only=True)
class ExchangeHttpClient(RpcClient):
  """HTTP transport for Hyperliquid exchange (signed) requests.

  `payload` is an `ExchangeRequest` in practice -- every `exchange` leaf method builds
  one -- but kept as the wider `Mapping[str, Any]` here to match `RpcClient.request`'s
  own signature; narrowing it would violate `RpcClient`'s Protocol contract (a
  `TypedDict` accepts a stricter set of values than `Mapping[str, Any]` does).
  """

  base_url: str
  http: HttpClient = field(default_factory=HttpClient)
  validate: bool = True

  @property
  def url(self) -> str:
    return f'{self.base_url.rstrip("/")}/exchange'

  async def request(self, payload: Mapping[str, Any]) -> Any:
    r = await self.http.request('POST', self.url, json=payload)
    if r.status_code != 200:
      raise ApiError(r.status_code, r.text)
    return response_adapter.validate_json(r.text) if self.validate else r.json()

  async def __aenter__(self):
    await self.http.__aenter__()
    return self

  async def __aexit__(self, exc_type, exc_value, traceback):
    await self.http.__aexit__(exc_type, exc_value, traceback)
