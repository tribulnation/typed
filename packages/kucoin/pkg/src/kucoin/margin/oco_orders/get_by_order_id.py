"""`GET /api/v3/hf/margin/oco-order/orderId` — Get OCO Order By OrderId."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp


class MarginOcoOrderSummary(TypedDict):
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
  """OCO order group status. Carried over from Spot's confirmed `OcoOrderSummary.status` enum -- not independently confirmed by this endpoint's own docs prose."""


_Type = MarginOcoOrderSummary | None
adapter = validator[_Type](_Type)  # type: ignore


class GetByOrderId(RpcEndpoint):
  """`Get OCO Order By OrderId` — mixed into `OcoOrders`, the product exposing `margin.oco_orders.get_by_order_id`."""

  async def get_by_order_id(
    self,
    *,
    order_id: str,
    validate: bool | None = None,
  ) -> MarginOcoOrderSummary | None:
    """Get a lightweight margin OCO order summary (no leg detail) by its order id, or `null` when no such order exists for this account. Distinct from Get OCO Order Detail By OrderId, which returns the full `orders[]` leg array.

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
      'GET',
      '/api/v3/hf/margin/oco-order/orderId',
      params=params,
      validator=adapter,
      validate=validate,
    )
