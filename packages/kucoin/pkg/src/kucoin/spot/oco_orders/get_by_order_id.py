"""`GET /api/v3/oco/order/{orderId}` — spot.oco_orders.get_by_order_id."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp


class OcoOrderSummary(TypedDict):
  """Lightweight OCO order summary, with no leg detail."""

  orderId: str
  """OCO order group id."""
  symbol: str
  """Trading pair."""
  clientOid: str
  """Client-provided order id, as supplied at placement."""
  orderTime: Timestamp
  """Time the OCO order was placed."""
  status: Literal['NEW', 'DONE', 'TRIGGERED', 'CANCELLED']
  """OCO order group status."""


_Type = OcoOrderSummary | None
adapter = validator[_Type](_Type)  # type: ignore


class GetByOrderId(RpcEndpoint):
  """`spot.oco_orders.get_by_order_id` — mixed into `OcoOrders`, the product exposing `spot.oco_orders.get_by_order_id`."""

  async def get_by_order_id(
    self,
    order_id: str,
    *,
    validate: bool | None = None,
  ) -> OcoOrderSummary | None:
    """Get a lightweight OCO order summary (no leg detail) by its order id. Distinct from Get OCO Order Detail By OrderId, which returns the full `orders[]` leg array and, per `notes` below, remains queryable after this endpoint stops returning the order.

    Args:
      order_id: The OCO order group's id, as returned by Add OCO Order.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'GET',
      f'/api/v3/oco/order/{order_id}',
      validator=adapter,
      validate=validate,
    )
