from typing_extensions import TypedDict
from bit2me.core.endpoint import RpcEndpoint


class TellerOrderCancelRequest(TypedDict):
  orderId: str
  description: str


class Cancel(RpcEndpoint):
  async def cancel(
    self,
    teller_order_cancel_request: TellerOrderCancelRequest,
    *,
    validate: bool | None = None,
  ):
    """Changes an order status from "waiting-user" to "cancelled" after the user accepting the transaction

    Args:
      teller_order_cancel_request: Order to cancel: the `orderId` from a previously created teller order, plus a `description` explaining the cancellation. Only applies while the order is in `waiting-user` status.
      validate: Whether to validate the response against the expected schema.

    References:
      - [Bit2Me API docs](https://api.bit2me.com/doc#tag/funding/POST/v1/teller/order/cancel)
    """
    return await self.authed_request(
      'POST',
      '/v1/teller/order/cancel',
      json=teller_order_cancel_request,
      validate=validate,
    )
