from typing_extensions import Literal
from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.types import TickerWindowEvent
from binance.core.endpoint.stream import StreamEndpoint


class TickerWindow(StreamEndpoint):
  """Individual symbol rolling window statistics stream"""

  def __call__(
    self,
    symbol: str,
    window: Literal['1h', '4h', '1d'],
    *,
    validate: bool | None = None,
  ) -> StreamManager[TickerWindowEvent]:
    """Individual symbol rolling window statistics stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.
      window: Rolling window size.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#individual-symbol-rolling-window-statistics-streams)
    """
    _validator = validator[TickerWindowEvent](TickerWindowEvent)
    return self.subscribe(
      f'{symbol.lower()}@ticker_{window}', validator=_validator, validate=validate
    )
