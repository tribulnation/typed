from typing_extensions import Literal, TypedDict
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.core import Timestamp
from binance.core.endpoint.stream import StreamEndpoint


class AvgPriceEvent(TypedDict):
  """Average price update for one symbol."""

  e: Literal['avgPrice']
  """Event type."""
  E: Timestamp
  """Event time."""
  s: str
  """Symbol."""
  i: str
  """Average price interval, e.g. `5m`."""
  w: str
  """Average price."""
  T: Timestamp
  """Last trade time."""


class AvgPrice(StreamEndpoint):
  """Average price stream"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[AvgPriceEvent]:
    """Average price stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#average-price)
    """
    _validator = validator[AvgPriceEvent](AvgPriceEvent)
    return self.subscribe(
      f'{symbol.lower()}@avgPrice', validator=_validator, validate=validate
    )
