from typing_extensions import Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class Candle(TypedDict):
  T: int
  """Candle close time, in milliseconds since epoch."""
  c: str
  """Close price, as a decimal string."""
  h: str
  """High price, as a decimal string."""
  i: Literal[
    '1m',
    '3m',
    '5m',
    '15m',
    '30m',
    '1h',
    '2h',
    '4h',
    '8h',
    '12h',
    '1d',
    '3d',
    '1w',
    '1M',
  ]
  """Candle interval."""
  l: str
  """Low price, as a decimal string."""
  n: int
  """Number of trades in the candle."""
  o: str
  """Open price, as a decimal string."""
  s: str
  """Coin the candle is for."""
  t: int
  """Candle open time, in milliseconds since epoch."""
  v: str
  """Traded volume in the candle, as a decimal string."""


class CandleSnapshotAction(TypedDict):
  type: Literal['candleSnapshot']
  coin: str
  endTime: int
  interval: Literal[
    '1m',
    '3m',
    '5m',
    '15m',
    '30m',
    '1h',
    '2h',
    '4h',
    '8h',
    '12h',
    '1d',
    '3d',
    '1w',
    '1M',
  ]
  startTime: int


adapter = pydantic.TypeAdapter(list[Candle])


class CandleSnapshot(InfoMixin):
  async def candle_snapshot(
    self,
    *,
    coin: str,
    end_time: int,
    interval: Literal[
      '1m',
      '3m',
      '5m',
      '15m',
      '30m',
      '1h',
      '2h',
      '4h',
      '8h',
      '12h',
      '1d',
      '3d',
      '1w',
      '1M',
    ],
    start_time: int,
  ) -> list[Candle]:
    """Retrieve OHLCV candles for a coin at a given interval over a time range.

    Args:
      coin: Coin to fetch candles for.
      end_time: End of the time range, in milliseconds since epoch.
      interval: Candle interval.
      start_time: Start of the time range, in milliseconds since epoch.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: CandleSnapshotAction = {
      'type': 'candleSnapshot',
      'coin': coin,
      'endTime': end_time,
      'interval': interval,
      'startTime': start_time,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
