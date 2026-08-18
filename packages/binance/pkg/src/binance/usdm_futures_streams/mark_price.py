from typing_extensions import NotRequired, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class MarkPriceEvent(TypedDict):
  """Mark price and funding rate for one symbol."""

  e: str
  """Event type."""
  E: Timestamp
  """Event time."""
  s: str
  """Symbol."""
  p: str
  """Mark price."""
  i: str
  """Index price."""
  P: str
  """Estimated settle price, only meaningful in the last hour before settlement."""
  r: str
  """Funding rate."""
  ap: str
  """Mark price moving average."""
  T: Timestamp
  """Next funding time."""
  st: NotRequired[int]
  """(After UM/CM stream-host migration) Symbol type: 1 = UM, 2 = CM."""


class MarkPrice(StreamEndpoint):
  """Mark price stream"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[MarkPriceEvent]:
    """Mark price stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/ws-streams/market#mark-price-stream)
    """
    _validator = validator[MarkPriceEvent](MarkPriceEvent)
    return self.subscribe(
      f'{symbol.lower()}@markPrice', validator=_validator, validate=validate
    )
