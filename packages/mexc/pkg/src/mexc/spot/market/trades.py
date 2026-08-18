from typing_extensions import TypedDict
from mexc.core import Timestamp, validator
from mexc.spot.core import ErrorResponse, SpotMixin

class TradesItem(TypedDict):
  id: int | str | None
  """Trade id; currently null on some live responses."""
  price: str
  """Trade price."""
  qty: str
  """Trade quantity."""
  quoteQty: str
  """Quote quantity."""
  time: Timestamp
  """Trade timestamp in milliseconds."""
  isBuyerMaker: bool
  """Whether the buyer was maker."""
  isBestMatch: bool
  """Whether this was the best match."""
  tradeType: str
  """Trade side label."""

Response: type[list[TradesItem] | ErrorResponse] = list[TradesItem] | ErrorResponse # type: ignore
adapter = validator(Response)

class Trades(SpotMixin):
  async def trades(
    self, *,
    symbol: str, limit: int | None = None, validate: bool | None = None,
  ) -> list[TradesItem]:
    """Return recent public trades for a spot symbol.

    Args:
      symbol: Spot symbol.
      limit: Maximum number of trades to return.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#recent-trades-list)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if limit is not None:
      params['limit'] = limit
    r = await self.request('GET', '/api/v3/trades', params=params)
    return self.output(r.text, adapter, validate)
