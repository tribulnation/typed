from typing_extensions import Literal, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class ContinuousKline(TypedDict):
  """The kline/candlestick itself."""

  t: Timestamp
  """Kline start time."""
  T: Timestamp
  """Kline close time."""
  i: Literal[
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
  ]
  """Interval."""
  f: int
  """First update ID."""
  L: int
  """Last update ID."""
  o: str
  """Open price."""
  c: str
  """Close price."""
  h: str
  """High price."""
  l: str
  """Low price."""
  v: str
  """Volume."""
  n: int
  """Number of trades."""
  x: bool
  """Whether this kline is closed."""
  q: str
  """Quote asset volume."""
  V: str
  """Taker buy volume."""
  Q: str
  """Taker buy quote asset volume."""
  B: str
  """Ignore."""


class ContinuousKlineEvent(TypedDict):
  """One continuous-contract kline/candlestick update."""

  e: str
  """Event type."""
  E: Timestamp
  """Event time."""
  ps: str
  """Pair."""
  ct: str
  """Contract type."""
  k: ContinuousKline


class ContinuousKlineEndpoint(StreamEndpoint):
  """Continuous contract kline/candlestick stream"""

  def __call__(
    self,
    pair: str,
    contractType: Literal[
      'perpetual', 'current_quarter', 'next_quarter', 'tradifi_perpetual'
    ],
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
    *,
    validate: bool | None = None,
  ) -> StreamManager[ContinuousKlineEvent]:
    """Continuous contract kline/candlestick stream

    Args:
      pair: Underlying trading pair, e.g. `BTCUSDT`.
      contractType: Contract type.
      interval: Kline interval.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market#continuous-contract-kline-candlestick-streams)
    """
    _validator = validator[ContinuousKlineEvent](ContinuousKlineEvent)
    return self.subscribe(
      f'{pair.lower()}_{contractType}@continuousKline_{interval}',
      validator=_validator,
      validate=validate,
    )
