from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class HistoricalTrade(TypedDict):
  """One historical market trade."""

  id: int
  """Trade id."""
  price: str
  """Trade price."""
  qty: str
  """Trade quantity, in base asset."""
  quoteQty: str
  """Trade quantity, in quote asset."""
  time: int
  """Trade time, in milliseconds since epoch."""
  isBuyerMaker: bool
  """Whether the buyer was the maker."""
  isRPITrade: NotRequired[bool]
  """Whether this trade involved a Retail Price Improvement (RPI) order."""


class HistoricalTrades(RpcEndpoint):
  """Older market trades for a symbol, paged backwards by trade id."""

  async def historical_trades(
    self,
    *,
    symbol: str,
    limit: int | None = None,
    from_id: int | None = None,
    validate: bool | None = None,
  ) -> list[HistoricalTrade]:
    """Older market trades for a symbol, paged backwards by trade id.

    Args:
      symbol: Trading symbol, e.g. BTCUSDT.
      limit: Number of trades to return.
      from_id: Trade id to fetch from. Omit to get the most recent trades.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#old-trades-lookup)
    """
    params: dict = {
      'symbol': symbol,
    }
    if limit is not None:
      params['limit'] = limit
    if from_id is not None:
      params['fromId'] = from_id
    _Response = list[HistoricalTrade]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/fapi/v1/historicalTrades',
      params=params,
      validator=_validator,
      validate=validate,
    )
