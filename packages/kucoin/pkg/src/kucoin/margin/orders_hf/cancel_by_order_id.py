"""`DELETE /api/v3/hf/margin/orders/{orderId}` — Cancel Order By OrderId."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class HfMarginCancelOrderResult(TypedDict):
  """Identifier of the order the cancellation request was accepted for."""

  orderId: str
  """System-generated id of the order being cancelled."""


_Type = HfMarginCancelOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class CancelByOrderId(RpcEndpoint):
  """`Cancel Order By OrderId` — mixed into `OrdersHf`, the product exposing `margin.orders_hf.cancel_by_order_id`."""

  async def cancel_by_order_id(
    self,
    order_id: str,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> HfMarginCancelOrderResult:
    """Cancel a single margin hf order by its system-generated order id. Sends a cancellation request only -- the cancellation is not guaranteed complete on response; confirm via Get by OrderId or the private order WebSocket feed.

    Args:
      order_id: System-generated id of the order to cancel.
      symbol: Trading pair symbol the order belongs to.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.authed_request(
      'DELETE',
      f'/api/v3/hf/margin/orders/{order_id}',
      params=params,
      validator=adapter,
      validate=validate,
    )
