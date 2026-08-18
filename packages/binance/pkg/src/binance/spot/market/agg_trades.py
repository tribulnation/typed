from datetime import timedelta
from typing_extensions import AsyncIterator, TypedDict
from typed_core.validation import validator
from typed_core.exceptions import LogicError
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


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


class AggTrades(RpcEndpoint):
  """Compressed/aggregate trades list"""

  async def agg_trades(
    self,
    *,
    symbol: str,
    from_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[AggTrade]:
    """Get compressed, aggregate trades. Trades that fill at the same time, from the same taker order, at the same price are aggregated into one entry with a combined quantity. If none of fromId, startTime, endTime are sent, the most recent aggregate trades are returned.

    Args:
      symbol: Symbol to query.
      from_id: Aggregate trade ID to fetch from, inclusive.
      start_time: Timestamp to fetch aggregate trades from, inclusive.
      end_time: Timestamp to fetch aggregate trades until, inclusive.
      limit: Number of aggregate trades to return.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md#compressedaggregate-trades-list)
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
      'GET', '/api/v3/aggTrades', params=params, validator=_validator, validate=validate
    )

  async def agg_trades_paged(
    self,
    *,
    symbol: str,
    from_id: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    allow_truncation: bool = False,
    validate: bool | None = None,
  ) -> AsyncIterator[list[AggTrade]]:
    """Yield successive pages of `agg_trades`.

    Moves the `start_time`–`end_time` window forwards by its own width and stops on the
    first empty window, or after `max_pages` pages when one is given.

    Every request spans the width the caller's own `start_time` and `end_time` state, so
    choose a window the venue answers in one response — at most `limit` rows. A full
    page is evidence the window was capped, and raises `LogicError` rather than walking
    past the rows that were left out; pass `allow_truncation=True` to accept the loss
    and keep going.
    """
    if start_time is None or end_time is None:
      raise ValueError(
        '`agg_trades_paged` walks a time window: pass both `start_time` and `end_time`'
      )
    lower = start_time
    upper = end_time
    width = upper - lower
    pages = 0
    while True:
      response = await self.agg_trades(
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
      if not allow_truncation and len(response) >= (
        limit if limit is not None else 500
      ):
        raise LogicError(
          f'`agg_trades_paged` requested the window {lower} to {upper} and the venue returned a full page of {len(response)} rows, so it may hold more; advancing would move past the rows that were left out. Narrow the window, or pass `allow_truncation=True` to accept the loss.'
        )
      lower = upper + timedelta(milliseconds=1)
      upper = lower + width
