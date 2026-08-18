"""`GET /api/v3/oco/order/details/{orderId}` — spot.oco_orders.get_detail."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp


class OcoLeg0(TypedDict):
  """One leg of an OCO order. Both legs share this exact shape."""

  id: str
  """This leg's own order id."""
  symbol: str
  """Trading pair."""
  side: Literal['buy', 'sell']
  """Order direction, shared by both legs."""
  price: str
  """This leg's limit price."""
  stopPrice: str
  """This leg's stop-trigger price. For the upper (position 0) leg, this echoes `price` rather than an independent trigger -- see `notes`."""
  size: str
  """This leg's order quantity."""
  status: str
  """This leg's own order status. KuCoin's machine-readable spec documents no enum or description for this field specifically (unlike the OCO group's own `status`); live captures observed only `NEW` and `CANCELLED`, consistent with but not proof of the group-level vocabulary, so left as a plain string rather than assuming the same closed set applies here."""


class OcoLeg1(TypedDict):
  """One leg of an OCO order. Both legs share this exact shape."""

  id: str
  """This leg's own order id."""
  symbol: str
  """Trading pair."""
  side: Literal['buy', 'sell']
  """Order direction, shared by both legs."""
  price: str
  """This leg's limit price."""
  stopPrice: str
  """This leg's stop-trigger price. For the lower (position 1) leg, this is the real, independent trigger price -- see `notes`."""
  size: str
  """This leg's order quantity."""
  status: str
  """This leg's own order status. KuCoin's machine-readable spec documents no enum or description for this field specifically (unlike the OCO group's own `status`); live captures observed only `NEW` and `CANCELLED`, consistent with but not proof of the group-level vocabulary, so left as a plain string rather than assuming the same closed set applies here."""


class OcoOrderDetail(TypedDict):
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
  orders: tuple[OcoLeg0, OcoLeg1]
  """The OCO's two linked leg orders. Position 0 is the upper leg (a plain limit order resting at `price`); position 1 is the lower leg (triggers at `stopPrice`, then executes as a limit order at its own `price`)."""


_Type = OcoOrderDetail
adapter = validator[_Type](_Type)  # type: ignore


class GetDetail(RpcEndpoint):
  """`spot.oco_orders.get_detail` — mixed into `OcoOrders`, the product exposing `spot.oco_orders.get_detail`."""

  async def get_detail(
    self,
    order_id: str,
    *,
    validate: bool | None = None,
  ) -> OcoOrderDetail:
    """Get an OCO order's full detail by its order id, including both leg orders. Unlike Get OCO Order By OrderId, this remains queryable for a terminal (cancelled/done) OCO order -- see `notes`.

    Args:
      order_id: The OCO order group's id, as returned by Add OCO Order.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'GET',
      f'/api/v3/oco/order/details/{order_id}',
      validator=adapter,
      validate=validate,
    )
