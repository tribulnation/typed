from typing_extensions import TypedDict
from mexc.spot.core import ErrorResponse, SpotMixin
from mexc.core import validator

class AvgPriceResponse(TypedDict):
  mins: int
  """Average price window in minutes."""
  price: str
  """Average price."""

Response: type[AvgPriceResponse | ErrorResponse] = AvgPriceResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class AvgPrice(SpotMixin):
  async def avg_price(self, *, symbol: str, validate: bool | None = None) -> AvgPriceResponse:
    """Return current average price for a spot symbol.

    Args:
      symbol: Spot symbol.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#current-average-price)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    r = await self.request('GET', '/api/v3/avgPrice', params=params)
    return self.output(r.text, adapter, validate)
