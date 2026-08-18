from datetime import timedelta
from typing_extensions import AsyncIterator, Literal
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.types import SpotCandle
from binance.core.endpoint.ws_rpc import WsRpcEndpoint


class Klines(WsRpcEndpoint):
  """Klines"""

  async def klines(
    self,
    *,
    symbol: str,
    interval: Literal[
      '1s',
      '1m',
      '3m',
      '5m',
      '15m',
      '30m',
      '1h',
      '2h',
      '4h',
      '6h',
      '8h',
      '12h',
      '1d',
      '3d',
      '1w',
      '1M',
    ],
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    time_zone: str | None = None,
    limit: int | None = None,
    validate: bool | None = None,
  ) -> list[SpotCandle]:
    """Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time. If startTime and endTime are not sent, the most recent klines are returned.

    Args:
      symbol: Symbol to query.
      interval: Kline interval.
      start_time: Timestamp to fetch klines from. Always interpreted in UTC regardless of `timeZone`.
      end_time: Timestamp to fetch klines until. Always interpreted in UTC regardless of `timeZone`.
      time_zone: Timezone kline intervals are interpreted in, as hours and minutes (e.g. '-1:00', '05:45') or just hours (e.g. '0', '8'). Accepted range is [-12:00, +14:00] inclusive. Does not affect `startTime`/`endTime`, which are always UTC.
      limit: Number of klines to return.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-api.md#klines)
    """
    params: dict = {
      'symbol': symbol,
      'interval': interval,
    }
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if time_zone is not None:
      params['timeZone'] = time_zone
    if limit is not None:
      params['limit'] = limit
    _Response = list[SpotCandle]
    _validator = validator[_Response](_Response)
    return await self.request(
      'klines', params=params, validator=_validator, validate=validate
    )

  async def klines_paged(
    self,
    *,
    symbol: str,
    interval: Literal[
      '1s',
      '1m',
      '3m',
      '5m',
      '15m',
      '30m',
      '1h',
      '2h',
      '4h',
      '6h',
      '8h',
      '12h',
      '1d',
      '3d',
      '1w',
      '1M',
    ],
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    time_zone: str | None = None,
    limit: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[list[SpotCandle]]:
    """Yield successive pages of `klines`.

    Moves the `start_time`–`end_time` window forwards by its own width and stops on the
    first empty window, or after `max_pages` pages when one is given.

    Every request spans the width the caller's own `start_time` and `end_time` state, so
    choose a window the venue answers in one response: it caps a wider one, and the walk
    moves past the rows that were left out.
    """
    if start_time is None or end_time is None:
      raise ValueError(
        '`klines_paged` walks a time window: pass both `start_time` and `end_time`'
      )
    lower = start_time
    upper = end_time
    width = upper - lower
    pages = 0
    while True:
      response = await self.klines(
        symbol=symbol,
        interval=interval,
        start_time=lower,
        end_time=upper,
        time_zone=time_zone,
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
