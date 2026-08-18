"""`GET /api/v1/hf/orders/{orderId}` — Get Order By OrderId."""

from typed_core.validation import validator
from kucoin.types import HfOrder
from kucoin.core import RpcEndpoint


_Type = HfOrder
adapter = validator[_Type](_Type)  # type: ignore


class GetByOrderId(RpcEndpoint):
  """`Get Order By OrderId` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.get_by_order_id`."""

  async def get_by_order_id(
    self,
    order_id: str,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> HfOrder:
    """Get a single spot hf order's full detail by its system-generated order id. Cancelled orders are queryable for 2 days after cancellation, filled orders for 7 days after filling.

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
      f'/api/v1/hf/orders/{order_id}',
      params=params,
      validator=adapter,
      validate=validate,
    )
