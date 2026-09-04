"""HTTP transport for `exchange` (wallet-signed) requests."""

from typing_extensions import Any, Mapping
from dataclasses import dataclass, field

from typed_core.exceptions import ApiError
from typed_core.http import HttpClient

from typed_hyperliquid.core.endpoint.rpc import RpcClient


@dataclass(kw_only=True)
class ExchangeHttpClient(RpcClient):
  """HTTP transport for Hyperliquid exchange (signed) requests.

  `payload` is an `ExchangeRequest` in practice -- every `exchange` leaf method builds
  one -- but kept as the wider `Mapping[str, Any]` here to match `RpcClient.request`'s
  own signature; narrowing it would violate `RpcClient`'s Protocol contract (a
  `TypedDict` accepts a stricter set of values than `Mapping[str, Any]` does).

  Returns the decoded `{status, response}` envelope verbatim -- unlike the pre-migration
  version of this class, it no longer validates it against a generic `ExchangeResponse`
  shape itself: `ExchangeCore.request` now does exactly one validation pass, against the
  endpoint's own specific `response_type`, so a second, looser pass here was redundant.
  """

  base_url: str
  http: HttpClient = field(default_factory=HttpClient)

  @property
  def url(self) -> str:
    return f'{self.base_url.rstrip("/")}/exchange'

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
