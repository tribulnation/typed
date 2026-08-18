from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.types import TickerEvent
from binance.core.endpoint.stream import StreamEndpoint


class Ticker(StreamEndpoint):
  """Individual symbol ticker stream"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[TickerEvent]:
    """Individual symbol ticker stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#individual-symbol-ticker-streams)
    """
    _validator = validator[TickerEvent](TickerEvent)
    return self.subscribe(
      f'{symbol.lower()}@ticker', validator=_validator, validate=validate
    )
