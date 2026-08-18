from typed_core.util import StreamManager
from typed_core.validation import validator
from binance.types import MiniTickerEvent
from binance.core.endpoint.stream import StreamEndpoint


class MiniTicker(StreamEndpoint):
  """Individual symbol mini ticker stream"""

  def __call__(
    self,
    symbol: str,
    *,
    validate: bool | None = None,
  ) -> StreamManager[MiniTickerEvent]:
    """Individual symbol mini ticker stream

    Args:
      symbol: Trading pair symbol, e.g. `BTCUSDT`. The venue requires stream names to use lowercase symbols on the wire.

    References:
      - [Official docs](https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md#individual-symbol-mini-ticker-stream)
    """
    _validator = validator[MiniTickerEvent](MiniTickerEvent)
    return self.subscribe(
      f'{symbol.lower()}@miniTicker', validator=_validator, validate=validate
    )
