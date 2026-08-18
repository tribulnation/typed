from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class CoinMForceOrder(TypedDict):
  """The liquidated order."""

  s: str
  """Symbol."""
  ps: str
  """Underlying pair."""
  S: Literal['BUY', 'SELL']
  """Order side."""
  o: Literal[
    'LIMIT',
    'MARKET',
    'STOP',
    'STOP_MARKET',
    'TAKE_PROFIT',
    'TAKE_PROFIT_MARKET',
    'TRAILING_STOP_MARKET',
  ]
  """Order type."""
  f: Literal['GTC', 'IOC', 'FOK', 'GTX']
  """Time in force."""
  q: str
  """Original quantity, in contracts."""
  p: str
  """Price."""
  ap: str
  """Average price."""
  X: Literal['NEW', 'PARTIALLY_FILLED', 'FILLED', 'CANCELED', 'EXPIRED']
  """Order status."""
  l: str
  """Order last filled quantity, in contracts."""
  z: str
  """Order filled accumulated quantity, in contracts."""
  T: Timestamp
  """Order trade time."""


class CoinMForceOrderEvent(TypedDict):
  """One forced-liquidation order."""

  e: Literal['forceOrder']
  """Event type."""
  E: Timestamp
  """Event time."""
  o: CoinMForceOrder
  st: NotRequired[Literal[1, 2]]
  """Symbol type: 1 = UM, 2 = CM. Added after the UM/CM stream-infrastructure migration; see notes."""


class ForceOrderArr(StreamEndpoint):
  """All market liquidation order streams"""

  def __call__(
    self,
    *,
    validate: bool | None = None,
  ) -> StreamManager[CoinMForceOrderEvent]:
    """All market liquidation order streams

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/ws-streams/~#all-market-liquidation-order-streams)
    """
    _validator = validator[CoinMForceOrderEvent](CoinMForceOrderEvent)
    return self.subscribe('!forceOrder@arr', validator=_validator, validate=validate)
