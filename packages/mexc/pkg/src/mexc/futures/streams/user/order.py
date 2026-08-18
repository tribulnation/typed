from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from typed_core.util import StreamManager
from typed_core.ws.streams import Stream
from mexc.core import validator, TypedDict
from mexc.futures.streams.core import AuthedStreamsMixin

class Order(TypedDict, total=False):
  orderId: str
  symbol: str
  category: int
  orderType: int
  side: int
  state: int
  price: Decimal
  vol: Decimal
  dealVol: Decimal
  dealAvgPrice: Decimal
  remainVol: Decimal
  createTime: datetime
  updateTime: datetime

validate_response = validator(Order)

@dataclass
class OrderStream(AuthedStreamsMixin):
  def order(self, *, validate: bool = True) -> StreamManager[Order, None, None]:
    """
    Subscribe to futures order updates.

    Args:
      validate: Validate pushed order payloads.

    References:
      - [MEXC futures WebSocket API](https://mexcdevelop.github.io/apidocs/contract_v1_en/#order-data)
    """
    return StreamManager(lambda: self._order_impl(validate=validate))

  async def _order_impl(self, *, validate: bool = True) -> Stream[Order, None, None]:
    stream = await self.authenticated_ws.subscribe('personal.order')
    async def parsed_stream():
      async for msg in stream:
        yield validate_response(msg) if self.validate(validate) else msg
    return Stream(reply=stream.reply, stream=parsed_stream(), unsubscribe=stream.unsubscribe)
