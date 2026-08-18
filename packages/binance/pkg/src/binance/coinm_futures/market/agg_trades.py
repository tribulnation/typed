from typing_extensions import TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class CoinMAggTrade(TypedDict):
  """One aggregate trade."""

  a: int
  """Aggregate trade ID."""
  p: str
  """Price."""
  q: str
  """Quantity, in contracts."""
  f: int
  """First trade ID in this aggregate."""
  l: int
  """Last trade ID in this aggregate."""
  T: int
  """Trade time, in milliseconds since epoch."""
  m: bool
  """Whether the buyer was the maker."""


class AggTrades(RpcEndpoint):
  """Get compressed, aggregate trades. Market trades that fill in 100ms with the same price and the same taking side are aggregated into a single row."""

  async def agg_trades(
    self,
    *,
    symbol: str,
    from_id: int | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[CoinMAggTrade]:
    """Get compressed, aggregate trades. Market trades that fill in 100ms with the same price and the same taking side are aggregated into a single row.

    Args:
      symbol: Symbol.
      from_id: ID to get aggregate trades from, inclusive.
      start_time: Timestamp to get aggregate trades from, inclusive, in milliseconds since epoch.
      end_time: Timestamp to get aggregate trades until, inclusive, in milliseconds since epoch.
      limit: Number of records to return.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/rest-api/market-data#compressed-aggregate-trades-list)
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
    _Response = list[CoinMAggTrade]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/dapi/v1/aggTrades',
      params=params,
      validator=_validator,
      validate=validate,
    )
