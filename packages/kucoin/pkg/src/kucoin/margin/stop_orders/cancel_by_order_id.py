"""`DELETE /api/v3/hf/margin/stop-order/cancel-by-id` — Cancel Stop Order By OrderId."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class CancelMarginStopOrderResult(TypedDict):
  cancelledOrderIds: list[str]
  """Ids of the stop orders cancelled by this call -- always a single-element array for this endpoint, since it targets one order id."""


_Type = CancelMarginStopOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class CancelByOrderId(RpcEndpoint):
  """`Cancel Stop Order By OrderId` — mixed into `StopOrders`, the product exposing `margin.stop_orders.cancel_by_order_id`."""

  async def cancel_by_order_id(
    self,
    *,
    order_id: str,
    validate: bool | None = None,
  ) -> CancelMarginStopOrderResult:
    """Request cancellation of a single untriggered margin stop order by its venue-assigned order id. Submission is acknowledged immediately; cancellation itself is processed sequentially by the matching engine, so confirm via a Get call or the private WebSocket stop-order channel.

    Args:
      order_id: Stop order id to cancel, as returned by Add Stop Order or Get Stop Orders List.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'orderId': order_id,
    }
    return await self.authed_request(
      'DELETE',
      '/api/v3/hf/margin/stop-order/cancel-by-id',
      params=params,
      validator=adapter,
      validate=validate,
    )
