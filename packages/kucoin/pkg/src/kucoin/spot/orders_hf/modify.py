"""`POST /api/v1/hf/orders/alter` — Modify Order."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class ModifyHfOrderByClientOid(TypedDict):
  """Modify a resting order identified by its client-provided order id."""

  symbol: str
  """Trading pair symbol the order belongs to."""
  clientOid: str
  """Client-provided id of the order to modify."""
  newPrice: str
  """Updated order price."""
  newSize: str
  """Updated order quantity."""


class ModifyHfOrderByOrderId(TypedDict):
  """Modify a resting order identified by its system-generated order id."""

  symbol: str
  """Trading pair symbol the order belongs to."""
  orderId: str
  """System-generated id of the order to modify."""
  newPrice: str
  """Updated order price."""
  newSize: str
  """Updated order quantity."""


class ModifyHfOrderResult(TypedDict):
  """Identifiers of the replacement order created by the modification."""

  newOrderId: str
  """System-generated id of the new (replacement) order."""
  clientOid: str
  """Client-provided order id, echoed back."""


_Type = ModifyHfOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class Modify(RpcEndpoint):
  """`Modify Order` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.modify`."""

  async def modify(
    self,
    body: ModifyHfOrderByOrderId | ModifyHfOrderByClientOid,
    *,
    validate: bool | None = None,
  ) -> ModifyHfOrderResult:
    """Atomically cancel a resting spot hf order and place a new one on the same trading pair with an updated price and/or size, returning the new order's identifiers. If the new size would fall below the quantity already filled, the original order is simply cancelled with no replacement.

    Args:
      body: Order to modify, identified by either `orderId` or `clientOid`, plus the new price and size.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/hf/orders/alter',
      json=body,
      validator=adapter,
      validate=validate,
    )
