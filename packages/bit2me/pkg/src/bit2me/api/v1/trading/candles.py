from decimal import Decimal
from typing_extensions import Literal
from bit2me.types import MillisTimestamp
from bit2me.core import timestamp
from bit2me.core.endpoint import RpcEndpoint
from typed_core.validation import validator

validate_response = validator(list[list[Decimal]])


class Candles(RpcEndpoint):
  async def __call__(
    self,
    *,
    symbol: str,
    interval: Literal[1, 5, 15, 30, 60, 240, 1440],
    start_time: MillisTimestamp,
    end_time: MillisTimestamp,
    limit: float,
    validate: bool | None = None,
  ) -> list[list[Decimal]]:
    """Get OHLCV (open, highest, lowest, close, volume) information. The last entry in the OHLCV array is for the current.

    Args:
      symbol: Market symbol to fetch OHLCV entries for.
      interval: The interval of entries in minutes: 1, 5, 15, 30, 60 (1 hour), 240 (4 hours), 1440 (1 day).
      start_time: Start of the time range to fetch OHLCV entries for, inclusive.
      end_time: End of the time range to fetch OHLCV entries for, inclusive.
      limit: The limit of `interval` entries (with an `interval` of 15 minutes and `limit` 4 the response is the last hour with 4 entries)
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-rest#tag/marketdata/GET/v1/trading/candle)
    """
    params: dict = {
      'symbol': symbol,
      'interval': interval,
      'startTime': timestamp.dump(start_time),
      'endTime': timestamp.dump(end_time),
      'limit': limit,
    }
    return await self.request(
      'GET',
      '/v1/trading/candle',
      params=params,
      validator=validate_response,
      validate=validate,
    )
