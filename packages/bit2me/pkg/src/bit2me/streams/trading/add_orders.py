from decimal import Decimal
from bit2me.core.endpoint import RpcEndpoint
from bit2me.core.transport.ws.trading import Reply
from typing_extensions import NotRequired, TypedDict
from bit2me.types import OrderSide, OrderType, PostOnlyParam, TimeInForce


class OrderRequest(TypedDict):
  """One order to place as part of the batch."""

  symbol: str
  """Market symbol to trade, for example `B2M/EUR`."""
  side: OrderSide
  type: OrderType
  price: NotRequired[Decimal]
  """Limit price; required for `limit` and `stop-limit` orders."""
  stopPrice: NotRequired[Decimal]
  """Trigger price; required for `stop-limit` orders."""
  amount: Decimal
  """Order volume, in base currency unless `amountInQuote` is set."""
  clientOrderId: NotRequired[str]
  """Caller-supplied identifier echoed back on the reply."""
  postOnly: NotRequired[PostOnlyParam]
  timeInForce: NotRequired[TimeInForce]
  amountInQuote: NotRequired[bool]
  """Whether `amount` is denominated in quote currency instead of base currency."""


class AddOrders(RpcEndpoint):
  async def add_orders(self, *, orders: list[OrderRequest]) -> Reply:
    """Authenticated Trading Spot WebSocket command `add-orders`.

    Args:
      orders: Orders to place in this batch, up to 20.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets#private-commands)
    """
    params: dict = {
      'orders': orders,
    }
    return await self.authed_request('POST', 'add-orders', json=params)
