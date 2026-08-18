from datetime import timedelta
from typing_extensions import AsyncIterator, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class AggTrade(TypedDict):
  """One compressed/aggregate trade."""

  a: int
  """Aggregate trade ID."""
  p: str
  """Price."""
  q: str
  """Quantity."""
  f: int
  """First trade ID in the aggregate."""
  l: int
  """Last trade ID in the aggregate."""
  T: Timestamp
  """Trade time."""
  m: bool
  """Whether the buyer was the maker."""
  M: bool
  """Whether the trade was the best price match."""


class TradesAggregate(WsRpcEndpoint):
  """Aggregate trades"""

  async def trades_aggregate(
    self,
    *,
    symbol: str,
    from_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[AggTrade]:
    """Get aggregate trades. An aggregate trade represents one or more individual trades: trades that fill at the same time, from the same taker order, at the same price are collected into one aggregate trade with the combined quantity. If none of fromId, startTime, endTime are sent, the most recent aggregate trades are returned.

    Args:
      symbol: Symbol to query.
      from_id: Aggregate trade ID to begin at. Cannot be used together with startTime/endTime.
      start_time: Timestamp to fetch aggregate trades from, inclusive.
      end_time: Timestamp to fetch aggregate trades until, inclusive.
      limit: Number of aggregate trades to return.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-api.md#aggregate-trades)
    """
    params: dict = {
      'symbol': symbol,
    }
    if from_id is not None:
      params['fromId'] = from_id
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    _Response = list[AggTrade]
    _validator = validator[_Response](_Response)
    return await self.request(
      'trades.aggregate', params=params, validator=_validator, validate=validate
    )

  async def trades_aggregate_paged(
    self,
    *,
    symbol: str,
    from_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[list[AggTrade]]:
    """Yield successive pages of `trades_aggregate`.

    Moves the `start_time`–`end_time` window forwards by its own width and stops on the
    first empty window, or after `max_pages` pages when one is given.

    Every request spans the width the caller's own `start_time` and `end_time` state, so
    choose a window the venue answers in one response: it caps a wider one, and the walk
    moves past the rows that were left out.
    """
    if start_time is None or end_time is None:
      raise ValueError(
        '`trades_aggregate_paged` walks a time window: pass both `start_time` and `end_time`'
      )
    lower = start_time
    upper = end_time
    width = upper - lower
    pages = 0
    while True:
      response = await self.trades_aggregate(
        symbol=symbol,
        from_id=from_id,
        start_time=lower,
        end_time=upper,
        limit=limit,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      if not response:
        break
      lower = upper + timedelta(milliseconds=1)
      upper = lower + width
