"""`DELETE /api/v1/stop-order/{orderId}` — spot.stop_orders.cancel_by_order_id."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class CancelStopOrderByOrderIdResult(TypedDict):
  cancelledOrderIds: list[str]
  """Ids of the stop orders cancelled by this call -- always a single-element array for this endpoint, since it targets one order id."""


_Type = CancelStopOrderByOrderIdResult
adapter = validator[_Type](_Type)  # type: ignore


class CancelByOrderId(RpcEndpoint):
  """`spot.stop_orders.cancel_by_order_id` — mixed into `StopOrders`, the product exposing `spot.stop_orders.cancel_by_order_id`."""

  async def cancel_by_order_id(
    self,
    order_id: str,
    *,
    validate: bool | None = None,
  ) -> CancelStopOrderByOrderIdResult:
    """Cancel a single untriggered stop order by its venue-assigned order id. Submission is acknowledged immediately; cancellation itself is processed sequentially by the matching engine, so confirm via Get Stop Order or the private WebSocket stop-order channel.

    Args:
      order_id: Stop order id to cancel, as returned by Add Stop Order or Get Stop Orders List.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'DELETE',
      f'/api/v1/stop-order/{order_id}',
      validator=adapter,
      validate=validate,
    )
