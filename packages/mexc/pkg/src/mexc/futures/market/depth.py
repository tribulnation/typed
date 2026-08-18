from typing_extensions import NotRequired, TypedDict
from mexc.core import Timestamp, validator
from mexc.futures.core import FuturesMixin

class DepthData(TypedDict):
  """Depth snapshot or incremental depth commit."""
  asks: list[tuple[float, float, int]]
  """Ask-side depth levels."""
  bids: list[tuple[float, float, int]]
  """Bid-side depth levels."""
  version: int
  """Depth version number."""
  timestamp: Timestamp
  """System timestamp in milliseconds."""

class DepthResponse(TypedDict):
  """Depth snapshot envelope"""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[DepthData]

adapter = validator(DepthResponse)

class Depth(FuturesMixin):
  async def depth(
    self, symbol: str, *,
    limit: int | None = None, validate: bool | None = None,
  ) -> DepthResponse:
    """Return a contract order book depth snapshot.

    Args:
      symbol: Contract symbol, for example BTC_USDT.
      limit: Depth tier/level count to return.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-the-contract-s-depth-information)
    """
    params = {}
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', '/api/v1/contract/depth/{symbol}'.replace('{symbol}', str(symbol)), params=params)
    return self.envelope_output(r.text, adapter, validate)
