from typing_extensions import NotRequired, TypedDict
from mexc.core import Timestamp, validator
from mexc.futures.core import FuturesMixin

class FairPriceData(TypedDict):
  """Fair price"""
  symbol: str
  """Contract symbol."""
  fairPrice: float
  """Fair price"""
  timestamp: Timestamp
  """System timestamp in milliseconds."""

class FairPriceResponse(TypedDict):
  """Fair price envelope"""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[FairPriceData]

adapter = validator(FairPriceResponse)

class FairPrice(FuturesMixin):
  async def fair_price(
    self, symbol: str, *,
    validate: bool | None = None,
  ) -> FairPriceResponse:
    """Return the current fair price for a contract.

    Args:
      symbol: Contract symbol, for example BTC_USDT.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-contract-fair-price)
    """
    params = {}
    r = await self.request('GET', '/api/v1/contract/fair_price/{symbol}'.replace('{symbol}', str(symbol)))
    return self.envelope_output(r.text, adapter, validate)
