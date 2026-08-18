from dataclasses import dataclass
from decimal import Decimal

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import StreamsMixin, Reply

class IndexPrice(TypedDict, total=False):
  symbol: str
  price: Decimal

validate_response = validator(IndexPrice)

@dataclass
class IndexPriceStream(StreamsMixin):
  def index_price(self, symbol: str, *, validate: bool = True) -> StreamManager[IndexPrice, Reply, Reply]:
    """
    Subscribe to index-price updates for one futures contract.

    Args:
      symbol: Futures contract symbol, for example `BTC_USDT`.
      validate: Validate pushed price payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#filter-subscription)
    """
    return StreamManager(lambda: self._index_price_impl(symbol, validate=validate))

  async def _index_price_impl(self, symbol: str, *, validate: bool = True) -> Stream[IndexPrice, Reply, Reply]:
    stream = await self.subscribe('index.price', {'symbol': symbol})
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
