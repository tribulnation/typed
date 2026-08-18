from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import StreamsMixin, Reply

class Deal(TypedDict, total=False):
  p: Decimal
  """Trade price."""
  v: Decimal
  """Trade volume."""
  T: int
  """Trade side code."""
  O: int
  """Open/close code."""
  M: int
  """Maker/taker code."""
  t: datetime
  """Trade timestamp in milliseconds."""

validate_response = validator(Deal)

@dataclass
class DealStream(StreamsMixin):
  def deal(self, symbol: str, *, validate: bool = True) -> StreamManager[Deal, Reply, Reply]:
    """
    Subscribe to futures trade updates for one contract.

    Args:
      symbol: Futures contract symbol, for example `BTC_USDT`.
      validate: Validate pushed trade payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#filter-subscription)
    """
    return StreamManager(lambda: self._deal_impl(symbol, validate=validate))

  async def _deal_impl(self, symbol: str, *, validate: bool = True) -> Stream[Deal, Reply, Reply]:
    stream = await self.subscribe('deal', {'symbol': symbol})
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
