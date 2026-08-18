"""`DELETE /api/v1/orders/{orderId}` — Cancel Order By OrderId."""

from typed_core.validation import validator
from kucoin.types import FuturesCancelResult
from kucoin.core import RpcEndpoint


_Type = FuturesCancelResult
adapter = validator[_Type](_Type)  # type: ignore


class CancelByOrderId(RpcEndpoint):
  """`Cancel Order By OrderId` — mixed into `Orders`, the product exposing `futures.orders.cancel_by_order_id`."""

  async def cancel_by_order_id(
    self,
    order_id: str,
    *,
    validate: bool | None = None,
  ) -> FuturesCancelResult:
    """Cancel a futures order (including a stop order) by its system-generated order id. The request is acknowledged immediately; the matching engine processes the cancellation asynchronously. Fails if the order is already filled or previously cancelled.

    Args:
      order_id: System-generated id of the order to cancel.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'DELETE',
      f'/api/v1/orders/{order_id}',
      validator=adapter,
      validate=validate,
    )
