"""`GET /api/v3/hf/margin/orders/{orderId}` — Get Order By OrderId."""

from typed_core.validation import validator
from kucoin.types import HfMarginOrder
from kucoin.core import RpcEndpoint


_Type = HfMarginOrder | None
adapter = validator[_Type](_Type)  # type: ignore


class GetByOrderId(RpcEndpoint):
  """`Get Order By OrderId` — mixed into `OrdersHf`, the product exposing `margin.orders_hf.get_by_order_id`."""

  async def get_by_order_id(
    self,
    order_id: str,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> HfMarginOrder | None:
    """Get a single margin hf order's full detail by its system-generated order id, or `null` when no such order exists for this account. Non-active (cancelled/filled) orders are only queryable within a 7-day window.

    Args:
      order_id: System-generated id of the order to look up.
      symbol: Trading pair symbol the order belongs to.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.authed_request(
      'GET',
      f'/api/v3/hf/margin/orders/{order_id}',
      params=params,
      validator=adapter,
      validate=validate,
    )
