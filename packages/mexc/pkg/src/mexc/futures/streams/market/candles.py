from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing_extensions import Literal

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import StreamsMixin, Reply

Interval = Literal['Min1', 'Min5', 'Min15', 'Min30', 'Min60', 'Hour4', 'Hour8', 'Day1', 'Week1', 'Month1']

class Candle(TypedDict, total=False):
  symbol: str
  interval: Interval
  a: Decimal
  """Total traded amount."""
  c: Decimal
  """Close price."""
  h: Decimal
  """High price."""
  l: Decimal
  """Low price."""
  o: Decimal
  """Open price."""
  q: Decimal
  """Total traded volume."""
  t: datetime
  """Window start time in seconds."""

validate_response = validator(Candle)

@dataclass
class Candles(StreamsMixin):
  def candles(
    self, symbol: str, interval: Interval, *, validate: bool = True,
  ) -> StreamManager[Candle, Reply, Reply]:
    """
    Subscribe to futures candlestick updates.

    Args:
      symbol: Futures contract symbol, for example `BTC_USDT`.
      interval: Candlestick interval.
      validate: Validate pushed candle payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#filter-subscription)
    """
    return StreamManager(lambda: self._candles_impl(symbol, interval, validate=validate))

  async def _candles_impl(
    self, symbol: str, interval: Interval, *, validate: bool = True,
  ) -> Stream[Candle, Reply, Reply]:
    stream = await self.subscribe('kline', {'symbol': symbol, 'interval': interval})
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
