from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class CoinMDiffDepthEvent(TypedDict):
  """Incremental order book update for one symbol."""

  e: Literal['depthUpdate']
  """Event type."""
  E: Timestamp
  """Event time."""
  T: Timestamp
  """Transaction time."""
  s: str
  """Symbol."""
  ps: str
  """Underlying pair."""
  U: int
  """First update ID in this event."""
  u: int
  """Final update ID in this event."""
  pu: int
  """Final update ID of the last stream push -- for sequencing against the previous message."""
  b: list[tuple[str, str]]
  """Bid price levels to update -- a `0` quantity removes the level."""
  a: list[tuple[str, str]]
  """Ask price levels to update -- a `0` quantity removes the level."""
  st: NotRequired[Literal[1, 2]]
  """Symbol type: 1 = UM, 2 = CM. Added after the UM/CM stream-infrastructure migration; see notes."""


class DiffDepth(StreamEndpoint):
  """Diff. book depth streams"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[CoinMDiffDepthEvent]:
    """Diff. book depth streams

    Args:
      symbol: Contract symbol, e.g. `BTCUSD_PERP`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/ws-streams/~#diff-book-depth-streams)
    """
    _validator = validator[CoinMDiffDepthEvent](CoinMDiffDepthEvent)
    return self.subscribe(
      f'{symbol.lower()}@depth', validator=_validator, validate=validate
    )
