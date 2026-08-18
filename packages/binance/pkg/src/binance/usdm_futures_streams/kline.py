from typing_extensions import Literal, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class Kline(TypedDict):
  """The kline/candlestick itself."""

  t: Timestamp
  """Kline start time."""
  T: Timestamp
  """Kline close time."""
  s: str
  """Symbol."""
  i: Literal[
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
  ]
  """Interval."""
  f: int
  """First trade ID."""
  L: int
  """Last trade ID."""
  o: str
  """Open price."""
  c: str
  """Close price."""
  h: str
  """High price."""
  l: str
  """Low price."""
  v: str
  """Base asset volume."""
  n: int
  """Number of trades."""
  x: bool
  """Whether this kline is closed."""
  q: str
  """Quote asset volume."""
  V: str
  """Taker buy base asset volume."""
  Q: str
  """Taker buy quote asset volume."""
  B: str
  """Ignore."""


class KlineEvent(TypedDict):
  """One kline/candlestick update."""

  e: str
  """Event type."""
  E: Timestamp
  """Event time."""
  s: str
  """Symbol."""
  k: Kline


class KlineEndpoint(StreamEndpoint):
  """Kline/candlestick stream"""

  def __call__(
    self,
    symbol: str,
    interval: Literal[
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
    *,
    validate: bool | None = None,
  ) -> StreamManager[KlineEvent]:
    """Kline/candlestick stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.
      interval: Kline interval.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market#kline-candlestick-streams)
    """
    _validator = validator[KlineEvent](KlineEvent)
    return self.subscribe(
      f'{symbol.lower()}@kline_{interval}', validator=_validator, validate=validate
    )
