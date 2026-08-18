from typing_extensions import Literal, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class CoinMContinuousKline(TypedDict):
  """The kline/candlestick itself."""

  t: Timestamp
  """Kline start time."""
  T: Timestamp
  """Kline close time."""
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
  """Volume, in contracts."""
  n: int
  """Number of trades."""
  x: bool
  """Whether this kline is closed."""
  q: str
  """Base asset volume."""
  V: str
  """Taker buy volume, in contracts."""
  Q: str
  """Taker buy base asset volume."""
  B: str
  """Ignore -- unused field, kept for wire compatibility."""


class CoinMContinuousKlineEvent(TypedDict):
  """One continuous-contract kline/candlestick update."""

  e: Literal['continuous_kline']
  """Event type."""
  E: Timestamp
  """Event time."""
  ps: str
  """Pair."""
  ct: Literal[
    'PERPETUAL',
    'CURRENT_QUARTER',
    'NEXT_QUARTER',
    'CURRENT_QUARTER_DELIVERING',
    'NEXT_QUARTER_DELIVERING',
    'PERPETUAL_DELIVERING',
  ]
  """Contract type."""
  k: CoinMContinuousKline


class ContinuousKline(StreamEndpoint):
  """Continuous contract kline/candlestick streams"""

  def __call__(
    self,
    pair: str,
    contractType: Literal['perpetual', 'current_quarter', 'next_quarter'],
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
  ) -> StreamManager[CoinMContinuousKlineEvent]:
    """Continuous contract kline/candlestick streams

    Args:
      pair: Underlying pair, e.g. `BTCUSD`.
      contractType: Contract type, templated into the channel in lowercase.
      interval: Kline interval.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/ws-streams/~#continuous-contract-kline-candlestick-streams)
    """
    _validator = validator[CoinMContinuousKlineEvent](CoinMContinuousKlineEvent)
    return self.subscribe(
      f'{pair.lower()}_{contractType}@continuousKline_{interval}',
      validator=_validator,
      validate=validate,
    )
