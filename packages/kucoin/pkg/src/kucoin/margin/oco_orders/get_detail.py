"""`GET /api/v3/hf/margin/oco-order/detail/orderId` — Get OCO Order Detail By OrderId."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp


class MarginOcoLeg0(TypedDict):
  """One leg of a margin OCO order. Both legs share this exact shape."""

  id: str
  """This leg's own order id."""
  symbol: str
  """Trading pair."""
  side: Literal['buy', 'sell']
  """Order direction, shared by both legs."""
  price: str
  """This leg's limit price."""
  stopPrice: str
  """This leg's stop-trigger price. For the upper (position 0) leg, Spot's confirmed behavior is that this echoes `price` rather than an independent trigger -- not independently re-confirmed for margin by a real capture this pass, since no real margin OCO order has ever existed on this account."""
  size: str
  """This leg's order quantity."""
  status: str
  """This leg's own order status. Left as a plain string rather than an enum, matching Spot's identical treatment -- KuCoin's docs never publish a closed set specifically for the leg-level status field, only the OCO group's own top-level `status`."""


class MarginOcoLeg1(TypedDict):
  """One leg of a margin OCO order. Both legs share this exact shape."""

  id: str
  """This leg's own order id."""
  symbol: str
  """Trading pair."""
  side: Literal['buy', 'sell']
  """Order direction, shared by both legs."""
  price: str
  """This leg's limit price."""
  stopPrice: str
  """This leg's stop-trigger price. For the lower (position 1) leg, Spot's confirmed behavior is that this is the real, independent trigger price."""
  size: str
  """This leg's order quantity."""
  status: str
  """This leg's own order status. Left as a plain string rather than an enum, matching Spot's identical treatment."""


class MarginOcoOrderDetail(TypedDict):
  orderId: str
  """OCO order group id."""
  symbol: str
  """Trading pair."""
  clientOid: str
  """Client-provided order id, as supplied at placement."""
  orderTime: Timestamp
  """Time the OCO order was placed."""
  status: Literal['NEW', 'DONE', 'TRIGGERED', 'CANCELLED']
  """OCO order group status. Carried over from Spot's confirmed `OcoOrderDetail.status` enum -- not independently confirmed by this endpoint's own docs prose."""
  orders: tuple[MarginOcoLeg0, MarginOcoLeg1]
  """The OCO's two linked leg orders. Position 0 is the upper leg (a plain limit order resting at `price`); position 1 is the lower leg (triggers at `stopPrice`, then executes as a limit order at its own `price`) -- same convention as Spot's `OcoLegs`."""


_Type = MarginOcoOrderDetail | None
adapter = validator[_Type](_Type)  # type: ignore


class GetDetail(RpcEndpoint):
  """`Get OCO Order Detail By OrderId` — mixed into `OcoOrders`, the product exposing `margin.oco_orders.get_detail`."""

  async def get_detail(
    self,
    *,
    order_id: str,
    validate: bool | None = None,
  ) -> MarginOcoOrderDetail | None:
    """Get a margin OCO order's full detail by its order id, including both leg orders, or `null` when no such order exists for this account.

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
      '/api/v3/hf/margin/oco-order/detail/orderId',
      params=params,
      validator=adapter,
      validate=validate,
    )
