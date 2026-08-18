from typing_extensions import NotRequired, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class BookTickerEvent(TypedDict):
  """Best bid/ask price and quantity for one symbol."""

  e: str
  """Event type."""
  u: int
  """Order book update ID."""
  E: Timestamp
  """Event time."""
  T: Timestamp
  """Transaction time."""
  s: str
  """Symbol."""
  ps: NotRequired[str]
  """(After UM/CM stream-host migration) Pair."""
  b: str
  """Best bid price."""
  B: str
  """Best bid quantity."""
  a: str
  """Best ask price."""
  A: str
  """Best ask quantity."""
  st: NotRequired[int]
  """(After UM/CM stream-host migration) Symbol type: 1 = UM, 2 = CM."""


class BookTicker(StreamEndpoint):
  """Individual symbol book ticker stream"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[BookTickerEvent]:
    """Individual symbol book ticker stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/public#individual-symbol-book-ticker-streams)
    """
    _validator = validator[BookTickerEvent](BookTickerEvent)
    return self.subscribe(
      f'{symbol.lower()}@bookTicker', validator=_validator, validate=validate
    )
