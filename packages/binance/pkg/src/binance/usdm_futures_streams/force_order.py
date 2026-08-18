from typing_extensions import Literal, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class LiquidationOrder(TypedDict):
  """The liquidation order itself."""

  s: str
  """Symbol."""
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
  f: Literal['GTC', 'IOC', 'FOK', 'GTX', 'GTD', 'RPI']
  """Time in force."""
  q: str
  """Original quantity."""
  p: str
  """Price."""
  ap: str
  """Average price."""
  X: str
  """Order status."""
  l: str
  """Order last filled quantity."""
  z: str
  """Order filled accumulated quantity."""
  T: Timestamp
  """Order trade time."""


class ForceOrderEvent(TypedDict):
  """Snapshot of the latest forced-liquidation order for one symbol."""

  e: str
  """Event type."""
  E: Timestamp
  """Event time."""
  o: LiquidationOrder


class ForceOrder(StreamEndpoint):
  """Liquidation order stream"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[ForceOrderEvent]:
    """Liquidation order stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market#liquidation-order-streams)
    """
    _validator = validator[ForceOrderEvent](ForceOrderEvent)
    return self.subscribe(
      f'{symbol.lower()}@forceOrder', validator=_validator, validate=validate
    )
