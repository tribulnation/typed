"""`DELETE /api/v3/hf/margin/oco-order/cancel-by-id` — Cancel OCO Order By OrderId."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class CancelMarginOcoOrderResult(TypedDict):
  cancelledOrderIds: list[str]
  """The two leg order ids belonging to the cancelled OCO order."""


_Type = CancelMarginOcoOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class CancelByOrderId(RpcEndpoint):
  """`Cancel OCO Order By OrderId` — mixed into `OcoOrders`, the product exposing `margin.oco_orders.cancel_by_order_id`."""

  async def cancel_by_order_id(
    self,
    *,
    order_id: str,
    validate: bool | None = None,
  ) -> CancelMarginOcoOrderResult:
    """Request cancellation of a single margin OCO order (both legs) by its order id. Submission is acknowledged immediately; cancellation itself is processed sequentially by the matching engine.

    Args:
      order_id: The OCO order group's id, as returned by Add OCO Order.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'orderId': order_id,
    }
    return await self.authed_request(
      'DELETE',
      '/api/v3/hf/margin/oco-order/cancel-by-id',
      params=params,
      validator=adapter,
      validate=validate,
    )
