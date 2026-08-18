from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class CoinMAggTradeEvent(TypedDict):
  """One aggregated trade for a symbol."""

  e: Literal['aggTrade']
  """Event type."""
  E: Timestamp
  """Event time."""
  a: int
  """Aggregate trade ID."""
  s: str
  """Symbol."""
  p: str
  """Price."""
  q: str
  """Quantity, in contracts."""
  f: int
  """First trade ID."""
  l: int
  """Last trade ID."""
  T: Timestamp
  """Trade time."""
  m: bool
  """Whether the buyer was the market maker."""
  st: NotRequired[Literal[1, 2]]
  """Symbol type: 1 = UM, 2 = CM. Added after the UM/CM stream-infrastructure migration; see notes."""


class AggTrade(StreamEndpoint):
  """Aggregate trade streams"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[CoinMAggTradeEvent]:
    """Aggregate trade streams

    Args:
      symbol: Contract symbol, e.g. `BTCUSD_PERP`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-coin-m-futures/api/ws-streams/~#aggregate-trade-streams)
    """
    _validator = validator[CoinMAggTradeEvent](CoinMAggTradeEvent)
    return self.subscribe(
      f'{symbol.lower()}@aggTrade', validator=_validator, validate=validate
    )
