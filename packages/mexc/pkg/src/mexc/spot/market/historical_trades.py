from typing_extensions import AsyncIterator, TypedDict
from mexc.core import Timestamp, validator
from mexc.spot.core import ErrorResponse, SpotMixin

class HistoricalTradesItem(TypedDict):
  id: int | str | None
  """Trade id; can be null on current live responses."""
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

Response: type[list[HistoricalTradesItem] | ErrorResponse] = list[HistoricalTradesItem] | ErrorResponse # type: ignore
adapter = validator(Response)

class HistoricalTrades(SpotMixin):
  async def historical_trades(
    self, *,
    symbol: str, limit: int | None = None, from_id: str | None = None,
    validate: bool | None = None,
  ) -> list[HistoricalTradesItem]:
    """Return older public spot trades for a symbol.

    Args:
      symbol: Spot symbol.
      limit: Maximum number of trades to return.
      from_id: Trade id to fetch from.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#old-trade-lookup)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if limit is not None:
      params['limit'] = limit
    if from_id is not None:
      params['fromId'] = from_id
    r = await self.request('GET', '/api/v3/historicalTrades', params=params)
    return self.output(r.text, adapter, validate)

  async def historical_trades_paged(
    self, *,
    symbol: str,
    limit: int | None = None,
    from_id: str | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[list[HistoricalTradesItem]]:
    """Yield historical trade pages by advancing the `fromId` cursor."""
    page = 0
    cursor = from_id
    while True:
      response = await self.historical_trades(symbol=symbol, limit=limit, from_id=cursor, validate=validate)
      yield response
      page += 1
      if max_pages is not None and page >= max_pages:
        break
      if not response or (limit is not None and len(response) < limit):
        break
      ids = [trade.get('id') for trade in response if trade.get('id') is not None]
      if not ids:
        break
      next_cursor = str(ids[-1])
      if next_cursor == cursor:
        break
      cursor = next_cursor
