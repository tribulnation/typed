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
  """Kline end (close) time."""
  s: str
  """Option symbol."""
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
  ]
  """Candle interval."""
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
  """Volume, in contracts."""
  n: int
  """Number of trades."""
  x: bool
  """Whether this candle has been completed."""
  q: str
  """Completed trade amount, in quote asset."""
  V: str
  """Taker completed trade volume, in contracts."""
  Q: str
  """Taker completed trade amount, in quote asset."""


class KlineEvent(TypedDict):
  """One kline/candlestick update."""

  e: Literal['kline']
  """Event type."""
  E: Timestamp
  """Event time."""
  s: str
  """Option symbol."""
  k: Kline


class KlineEndpoint(StreamEndpoint):
  """Kline/candlestick streams"""

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
    ],
    *,
    validate: bool | None = None,
  ) -> StreamManager[KlineEvent]:
    """Kline/candlestick streams

    Args:
      symbol: Option symbol, e.g. `BTC-250627-50000-C`.
      interval: Kline interval.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-options/api/ws-streams/market#kline-candlestick-streams)
    """
    _validator = validator[KlineEvent](KlineEvent)
    return self.subscribe(
      f'{symbol.lower()}@kline_{interval}', validator=_validator, validate=validate
    )
