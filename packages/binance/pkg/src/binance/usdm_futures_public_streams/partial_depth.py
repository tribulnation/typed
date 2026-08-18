from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class PartialDepthEvent(TypedDict):
  """Top `levels` bids and asks for one symbol."""

  e: str
  """Event type."""
  E: Timestamp
  """Event time."""
  T: Timestamp
  """Transaction time."""
  s: str
  """Symbol."""
  U: int
  """First update ID in event."""
  u: int
  """Final update ID in event."""
  pu: int
  """Final update ID in the last stream event (i.e. this event's `u` minus one push)."""
  b: list[tuple[str, str]]
  """Bids to be updated, best (highest) first."""
  a: list[tuple[str, str]]
  """Asks to be updated, best (lowest) first."""
  ps: NotRequired[str]
  """(After UM/CM stream-host migration) Pair symbol."""
  st: NotRequired[int]
  """(After UM/CM stream-host migration) Symbol type: 1 = UM, 2 = CM."""


class PartialDepth(StreamEndpoint):
  """Partial book depth stream"""

  def __call__(
    self,
    symbol: str,
    levels: Literal[5, 10, 20],
    speed: Literal[100, 250, 500],
    *,
    validate: bool | None = None,
  ) -> StreamManager[PartialDepthEvent]:
    """Partial book depth stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.
      levels: Number of bid/ask levels to push.
      speed: Update speed, in milliseconds.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/public#partial-book-depth-streams)
    """
    _validator = validator[PartialDepthEvent](PartialDepthEvent)
    return self.subscribe(
      f'{symbol.lower()}@depth{levels}@{speed}ms',
      validator=_validator,
      validate=validate,
    )
