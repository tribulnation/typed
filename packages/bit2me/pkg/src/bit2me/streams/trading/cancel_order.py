from bit2me.core.endpoint import RpcEndpoint
from bit2me.core.transport.ws.trading import Reply


class CancelOrder(RpcEndpoint):
  async def cancel_order(self, *, order_id: str) -> Reply:
    """Authenticated Trading Spot WebSocket command `cancel-order`.

    Args:
      order_id: Identifier of the order to cancel.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets#private-commands)
    """
    params: dict = {
      'orderId': order_id,
    }
    return await self.authed_request('POST', 'cancel-order', json=params)
