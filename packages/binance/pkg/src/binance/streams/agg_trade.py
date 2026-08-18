from typing_extensions import Literal, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class AggTradeEvent(TypedDict):
  """One aggregated taker trade."""

  e: Literal['aggTrade']
  """Event type."""
  E: Timestamp
  """Event time."""
  s: str
  """Symbol."""
  a: int
  """Aggregate trade ID."""
  p: str
  """Price."""
  q: str
  """Quantity."""
  f: int
  """First trade ID aggregated into this trade."""
  l: int
  """Last trade ID aggregated into this trade."""
  T: Timestamp
  """Trade time."""
  m: bool
  """Whether the buyer was the market maker."""
  M: bool
  """Ignore."""


class AggTrade(StreamEndpoint):
  """Aggregate trade stream"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[AggTradeEvent]:
    """Aggregate trade stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#aggregate-trade-streams)
    """
    _validator = validator[AggTradeEvent](AggTradeEvent)
    return self.subscribe(
      f'{symbol.lower()}@aggTrade', validator=_validator, validate=validate
    )
