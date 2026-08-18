"""`streams.market_data.ohlc` -- WebSocket channel subscription."""

from typing_extensions import Literal, NotRequired
from typed_core.validation import TypedDict, validator
from typed_core.util import StreamManager
from ...core.endpoint.stream import StreamEndpoint


class OhlcCandle(TypedDict):
  """One symbol's OHLC candle for the subscribed interval."""

  symbol: str
  """The symbol of the currency pair, e.g. `"BTC/USD"`."""
  open: float
  """The opening trade price within the interval."""
  high: float
  """The highest trade price within the interval."""
  low: float
  """The lowest trade price within the interval."""
  close: float
  """The last trade price within the interval."""
  vwap: float
  """Volume weighted average trade price within the interval."""
  trades: int
  """Number of trades within the interval."""
  volume: float
  """Total traded volume, in base currency terms, within the interval."""
  interval_begin: str
  """RFC3339 timestamp of the start of the interval."""
  interval: int
  """The timeframe of this candle's interval, in minutes."""
  timestamp: NotRequired[str]
  """RFC3339 timestamp of the start of the interval. Deprecated -- use `interval_begin`."""


class OhlcMessage(TypedDict):
  """An `ohlc` channel push."""

  channel: Literal['ohlc']
  """The channel this push belongs to."""
  type: Literal['snapshot', 'update']
  """Whether this push is the initial snapshot or an incremental update."""
  timestamp: NotRequired[str]
  """RFC3339 timestamp of this push. Not documented in the channel's field reference, but present on every worked example on the doc page."""
  data: list[OhlcCandle]
  """A list of candle events."""


validate_ohlc = validator(OhlcMessage)


class Ohlc(StreamEndpoint):
  """`streams.market_data.ohlc`."""

  def ohlc(
    self,
    *,
    symbol: list[str],
    interval: Literal[1, 5, 15, 30, 60, 240, 1440, 10080, 21600] | None = None,
    snapshot: bool | None = None,
  ) -> StreamManager[OhlcMessage, object, object]:
    """Subscribe to Open/High/Low/Close (OHLC) candle data at a given interval for one or more currency pairs. Updates are generated on trade events.

    Args:
      symbol: Currency pairs to subscribe to, e.g. `["BTC/USD", "MATIC/GBP"]`.
      interval: The interval timeframe, in minutes.
      snapshot: Request a snapshot after subscribing.

    References:
      - [Official docs](https://docs.kraken.com/exchange/api-reference/spot-websocket-v2/ohlc)
    """
    params: dict = {
      'symbol': symbol,
    }
    if interval is not None:
      params['interval'] = interval
    if snapshot is not None:
      params['snapshot'] = snapshot

    return self.subscribe('ohlc', params, validator=validate_ohlc)
