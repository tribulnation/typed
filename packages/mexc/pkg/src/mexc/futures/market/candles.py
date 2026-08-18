from typing_extensions import Literal, NotRequired, TypedDict
from mexc.core import TimestampSeconds, timestamp_s as ts_s, validator
from mexc.futures.core import FuturesMixin

class CandlesData(TypedDict):
  """K-line series, with each array index representing the same candle across fields."""
  time: list[TimestampSeconds]
  """Candle open times in seconds."""
  open: list[float]
  """Opening prices."""
  close: list[float]
  """Closing prices."""
  high: list[float]
  """Highest prices."""
  low: list[float]
  """Lowest prices."""
  vol: list[float]
  """Contract volumes."""
  amount: list[float]
  """Quote amounts."""
  realOpen: list[float]
  """Live API real opening prices."""
  realClose: list[float]
  """Live API real closing prices."""
  realHigh: list[float]
  """Live API real highest prices."""
  realLow: list[float]
  """Live API real lowest prices."""

class CandlesResponse(TypedDict):
  """Contract K-line envelope"""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[CandlesData]

adapter = validator(CandlesResponse)

class Candles(FuturesMixin):
  async def candles(
    self, symbol: str, *,
    interval: Literal['Min1', 'Min5', 'Min15', 'Min30', 'Min60', 'Hour4', 'Hour8', 'Day1', 'Week1', 'Month1'] | None = None,
    start: TimestampSeconds | None = None, end: TimestampSeconds | None = None,
    validate: bool | None = None,
  ) -> CandlesResponse:
    """Return contract K-line/candlestick series for a symbol and optional time window.

    Args:
      symbol: Contract symbol, for example BTC_USDT.
      interval: K-line interval: Min1, Min5, Min15, Min30, Min60, Hour4, Hour8, Day1, Week1, or Month1.
      start: Start timestamp in seconds.
      end: End timestamp in seconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#k-line-data)
    """
    params = {}
    if interval is not None:
      params['interval'] = interval
    if start is not None:
      params['start'] = ts_s.dump(start)
    if end is not None:
      params['end'] = ts_s.dump(end)
    r = await self.request('GET', '/api/v1/contract/kline/{symbol}'.replace('{symbol}', str(symbol)), params=params)
    return self.envelope_output(r.text, adapter, validate)
