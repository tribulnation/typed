from bit2me.core.endpoint import RpcEndpoint
from bit2me.core.transport.ws.trading import Reply
from bit2me.types import OrderSide


class CancelAllOrders(RpcEndpoint):
  async def cancel_all_orders(
    self,
    *,
    symbol: str | None = None,
    side: OrderSide | None = None,
  ) -> Reply:
    """Authenticated Trading Spot WebSocket command `cancel-all-orders`.

    Args:
      symbol: Market symbol to scope the cancellation to; omit to cancel across every symbol.
      side: Order direction to scope the cancellation to; omit to cancel both sides.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets#private-commands)
    """
    params: dict = {}
    if symbol is not None:
      params['symbol'] = symbol
    if side is not None:
      params['side'] = side
    return await self.authed_request('POST', 'cancel-all-orders', json=params)
