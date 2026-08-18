from bit2me.core.endpoint import RpcEndpoint
from bit2me.core.transport.ws.trading import Reply


class CancelOrders(RpcEndpoint):
  async def cancel_orders(self, *, orders_id: list[str]) -> Reply:
    """Authenticated Trading Spot WebSocket command `cancel-orders`.

    Args:
      orders_id: Identifiers of the orders to cancel, up to 20.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets#private-commands)
    """
    params: dict = {
      'ordersId': orders_id,
    }
    return await self.authed_request('POST', 'cancel-orders', json=params)
