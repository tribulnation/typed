from typing_extensions import Literal, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class TradeEvent(TypedDict):
  """One executed trade."""

  e: Literal['trade']
  """Event type."""
  E: Timestamp
  """Event time."""
  s: str
  """Symbol."""
  t: int
  """Trade ID."""
  p: str
  """Price."""
  q: str
  """Quantity."""
  T: Timestamp
  """Trade time."""
  m: bool
  """Whether the buyer was the market maker."""
  M: bool
  """Ignore."""


class Trade(StreamEndpoint):
  """Trade stream"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[TradeEvent]:
    """Trade stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#trade-streams)
    """
    _validator = validator[TradeEvent](TradeEvent)
    return self.subscribe(
      f'{symbol.lower()}@trade', validator=_validator, validate=validate
    )
