from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class CoinMMiniTickerEvent(TypedDict):
  """24hr rolling-window mini-ticker statistics for one symbol."""

  e: Literal['24hrMiniTicker']
  """Event type."""
  E: Timestamp
  """Event time."""
  s: str
  """Symbol."""
  ps: str
  """Underlying pair."""
  c: str
  """Close price."""
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
  st: NotRequired[Literal[1, 2]]
  """Symbol type: 1 = UM, 2 = CM. Added after the UM/CM stream-infrastructure migration; see notes."""


class MiniTickerArr(StreamEndpoint):
  """All market mini tickers stream"""

  def __call__(
    self,
    *,
    validate: bool | None = None,
  ) -> StreamManager[list[CoinMMiniTickerEvent]]:
    """All market mini tickers stream

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/ws-streams/~#all-market-mini-tickers-stream)
    """
    _validator = validator[list[CoinMMiniTickerEvent]](list[CoinMMiniTickerEvent])
    return self.subscribe('!miniTicker@arr', validator=_validator, validate=validate)
