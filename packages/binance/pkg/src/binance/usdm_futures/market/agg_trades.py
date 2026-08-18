from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class AggregateTrade(TypedDict):
  """One aggregate (compressed) trade."""

  a: int
  """Aggregate trade id."""
  p: str
  """Price."""
  q: str
  """Quantity."""
  nq: NotRequired[str]
  """Quantity, excluding the portion filled by RPI orders."""
  f: int
  """First trade id in this aggregate."""
  l: int
  """Last trade id in this aggregate."""
  T: int
  """Trade time, in milliseconds since epoch."""
  m: bool
  """Whether the buyer was the maker."""


class AggTrades(RpcEndpoint):
  """Compressed, aggregate market trades. Trades that fill at the same time, at the same price, from the same taker order are aggregated into one row."""

  async def agg_trades(
    self,
    *,
    symbol: str,
    from_id: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[AggregateTrade]:
    """Compressed, aggregate market trades. Trades that fill at the same time, at the same price, from the same taker order are aggregated into one row.

    Args:
      symbol: Trading symbol, e.g. BTCUSDT.
      from_id: Aggregate trade id to fetch from. Omit to get the most recent trades.
      start_time: Start time, in milliseconds since epoch.
      end_time: End time, in milliseconds since epoch.
      limit: Number of trades to return.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#compressed-aggregate-trades-list)
    """
    params: dict = {
      'symbol': symbol,
    }
    if from_id is not None:
      params['fromId'] = from_id
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if limit is not None:
      params['limit'] = limit
    _Response = list[AggregateTrade]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/fapi/v1/aggTrades',
      params=params,
      validator=_validator,
      validate=validate,
    )
