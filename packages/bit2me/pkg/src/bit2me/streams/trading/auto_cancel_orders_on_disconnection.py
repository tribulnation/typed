from bit2me.core.endpoint import RpcEndpoint
from bit2me.core.transport.ws.trading import Reply
from typing_extensions import Literal, TypedDict


class DeleteLastWindow(TypedDict):
  """Restricts cancellation to orders created within a trailing time window; omit to cancel every open order."""

  value: int
  """Size of the trailing time window."""
  unit: Literal['s', 'm', 'h', 'd']
  """Unit of `value`."""


class AutoCancelOrdersOnDisconnection(RpcEndpoint):
  async def auto_cancel_orders_on_disconnection(
    self,
    *,
    symbol: str | None = None,
    timeout: int,
    delete_last: DeleteLastWindow | None = None,
  ) -> Reply:
    """Authenticated Trading Spot WebSocket command `auto-cancel-orders-on-disconnection`.

    Args:
      symbol: Market symbol to scope the auto-cancel to; omit to scope to every symbol.
      timeout: Seconds to wait for another `auto-cancel-orders-on-disconnection` command before the trigger fires. Zero or negative disables the auto-cancel.
      delete_last: Restricts cancellation to orders created within a trailing time window; omit to cancel every open order.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/trading-spot-websockets#private-commands)
    """
    params: dict = {
      'timeout': timeout,
    }
    if symbol is not None:
      params['symbol'] = symbol
    if delete_last is not None:
      params['deleteLast'] = delete_last
    return await self.authed_request(
      'POST', 'auto-cancel-orders-on-disconnection', json=params
    )
