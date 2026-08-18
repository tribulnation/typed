from decimal import Decimal
from bit2me.core.endpoint import RpcEndpoint
from bit2me.core.transport.ws.trading import Reply
from bit2me.types import OrderSide, OrderType, PostOnlyParam, TimeInForce


class AddOrder(RpcEndpoint):
  async def add_order(
    self,
    *,
    symbol: str,
    side: OrderSide,
    type: OrderType,
    price: Decimal | None = None,
    stop_price: Decimal | None = None,
    amount: Decimal,
    client_order_id: str | None = None,
    post_only: PostOnlyParam | None = None,
    time_in_force: TimeInForce | None = None,
    amount_in_quote: bool | None = None,
  ) -> Reply:
    """Authenticated Trading Spot WebSocket command `add-order`.

    Args:
      symbol: Market symbol to trade, for example `B2M/EUR`.
      side: Order direction.
      type: Order type.
      price: Limit price; required for `limit` and `stop-limit` orders.
      stop_price: Trigger price; required for `stop-limit` orders.
      amount: Order volume, in base currency unless `amountInQuote` is set.
      client_order_id: Caller-supplied identifier echoed back on the reply.
      post_only: Command parameter.
      time_in_force: Command parameter.
      amount_in_quote: Whether `amount` is denominated in quote currency instead of base currency.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets#private-commands)
    """
    params: dict = {
      'symbol': symbol,
      'side': side,
      'type': type,
      'amount': amount,
    }
    if price is not None:
      params['price'] = price
    if stop_price is not None:
      params['stopPrice'] = stop_price
    if client_order_id is not None:
      params['clientOrderId'] = client_order_id
    if post_only is not None:
      params['postOnly'] = post_only
    if time_in_force is not None:
      params['timeInForce'] = time_in_force
    if amount_in_quote is not None:
      params['amountInQuote'] = amount_in_quote
    return await self.authed_request('POST', 'add-order', json=params)
