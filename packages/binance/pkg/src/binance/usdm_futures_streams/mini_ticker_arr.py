from typing_extensions import NotRequired, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class MiniTickerEventItem(TypedDict):
  """24hr rolling-window mini-ticker statistics for one symbol."""

  e: str
  """Event type."""
  E: Timestamp
  """Event time."""
  s: str
  """Symbol."""
  c: str
  """Close price."""
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
  ps: NotRequired[str]
  """(After UM/CM stream-host migration) Pair symbol."""
  st: NotRequired[int]
  """(After UM/CM stream-host migration) Symbol type: 1 = UM, 2 = CM."""


class MiniTickerArr(StreamEndpoint):
  """All market mini tickers stream"""

  def __call__(
    self,
    *,
    validate: bool | None = None,
  ) -> StreamManager[list[MiniTickerEventItem]]:
    """All market mini tickers stream

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market#all-market-mini-tickers-stream)
    """
    _validator = validator[list[MiniTickerEventItem]](list[MiniTickerEventItem])
    return self.subscribe('!miniTicker@arr', validator=_validator, validate=validate)
