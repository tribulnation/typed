from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMHistoricalTrade(TypedDict):
  """One historical market trade."""

  id: int
  """Trade ID."""
  price: str
  """Trade price."""
  qty: str
  """Trade quantity, in contracts."""
  baseQty: str
  """Trade quantity, in base asset."""
  time: int
  """Trade time, in milliseconds since epoch."""
  isBuyerMaker: bool
  """Whether the buyer was the maker."""


class HistoricalTrades(RpcEndpoint):
  """Older market trades for a symbol. Only the last one month of data is available."""

  async def historical_trades(
    self,
    *,
    symbol: str,
    limit: int | None = None,
    from_id: int | None = None,
    validate: bool | None = None,
  ) -> list[CoinMHistoricalTrade]:
    """Older market trades for a symbol. Only the last one month of data is available.

    Args:
      symbol: Symbol.
      limit: Number of trades to return.
      from_id: Trade ID to fetch from. Omit to get the most recent trades.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#old-trades-lookup)
    """
    params: dict = {
      'symbol': symbol,
    }
    if limit is not None:
      params['limit'] = limit
    if from_id is not None:
      params['fromId'] = from_id
    _Response = list[CoinMHistoricalTrade]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/dapi/v1/historicalTrades',
      params=params,
      validator=_validator,
      validate=validate,
    )
