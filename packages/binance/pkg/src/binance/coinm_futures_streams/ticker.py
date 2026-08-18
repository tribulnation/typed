from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class CoinMTickerEvent(TypedDict):
  """Full 24hr rolling-window ticker statistics for one symbol."""

  e: Literal['24hrTicker']
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
  """Total traded volume, in contracts."""
  q: str
  """Total traded base asset volume."""
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
  ps: str
  """Underlying pair."""
  st: NotRequired[Literal[1, 2]]
  """Symbol type: 1 = UM, 2 = CM. Added after the UM/CM stream-infrastructure migration; see notes."""


class Ticker(StreamEndpoint):
  """Individual symbol ticker streams"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[CoinMTickerEvent]:
    """Individual symbol ticker streams

    Args:
      symbol: Contract symbol, e.g. `BTCUSD_PERP`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/ws-streams/~#individual-symbol-ticker-streams)
    """
    _validator = validator[CoinMTickerEvent](CoinMTickerEvent)
    return self.subscribe(
      f'{symbol.lower()}@ticker', validator=_validator, validate=validate
    )
