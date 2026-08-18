from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class CoinMBookTickerEvent(TypedDict):
  """Best bid/ask price and quantity update for one symbol's order book."""

  e: Literal['bookTicker']
  """Event type."""
  u: int
  """Order book update ID."""
  s: str
  """Symbol."""
  ps: str
  """Underlying pair."""
  b: str
  """Best bid price."""
  B: str
  """Best bid quantity."""
  a: str
  """Best ask price."""
  A: str
  """Best ask quantity."""
  T: Timestamp
  """Transaction time."""
  E: Timestamp
  """Event time."""
  st: NotRequired[Literal[1, 2]]
  """Symbol type: 1 = UM, 2 = CM. Added after the UM/CM stream-infrastructure migration; see notes."""


class BookTicker(StreamEndpoint):
  """Individual symbol book ticker streams"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[CoinMBookTickerEvent]:
    """Individual symbol book ticker streams

    Args:
      symbol: Contract symbol, e.g. `BTCUSD_PERP`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/ws-streams/~#individual-symbol-book-ticker-streams)
    """
    _validator = validator[CoinMBookTickerEvent](CoinMBookTickerEvent)
    return self.subscribe(
      f'{symbol.lower()}@bookTicker', validator=_validator, validate=validate
    )
