from typing_extensions import NotRequired, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class TickerEventResponsemessage(TypedDict):
  """24hr rolling-window ticker statistics for one symbol."""

  e: str
  """Event type."""
  E: Timestamp
  """Event time."""
  s: str
  """Symbol."""
  p: str
  """Price change."""
  P: str
  """Price change percent."""
  w: str
  """Weighted average price."""
  c: str
  """Last price."""
  Q: str
  """Last quantity."""
  o: str
  """Open price."""
  h: str
  """High price."""
  l: str
  """Low price."""
  v: str
  """Total traded base asset volume."""
  q: str
  """Total traded quote asset volume."""
  O: Timestamp
  """Statistics open time."""
  C: Timestamp
  """Statistics close time."""
  F: int
  """First trade ID."""
  L: int
  """Last trade ID."""
  n: int
  """Total number of trades."""
  ps: NotRequired[str]
  """(After UM/CM stream-host migration) Pair symbol."""
  st: NotRequired[int]
  """(After UM/CM stream-host migration) Symbol type: 1 = UM, 2 = CM."""


class Ticker(StreamEndpoint):
  """Individual symbol ticker stream"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[TickerEventResponsemessage]:
    """Individual symbol ticker stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market#individual-symbol-ticker-streams)
    """
    _validator = validator[TickerEventResponsemessage](TickerEventResponsemessage)
    return self.subscribe(
      f'{symbol.lower()}@ticker', validator=_validator, validate=validate
    )
