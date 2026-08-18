"""`spot.trading.cancel_order` -- private Spot endpoint."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class OrderCancelled(TypedDict):
  """Result of a cancel request."""

  count: NotRequired[int]
  """Number of orders cancelled."""
  pending: NotRequired[bool]
  """If true, orders are pending cancellation."""


validate_cancel_order = validator(OrderCancelled)


class CancelOrder(RpcEndpoint):
  """`spot.trading.cancel_order`."""

  async def cancel_order(
    self,
    *,
    txid: str | int | None = None,
    cl_ord_id: str | None = None,
  ) -> OrderCancelled:
    """Cancel a particular open order (or set of open orders sharing a `userref`) by `txid`, `userref` or `cl_ord_id`.

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` or `Orders and trades - Cancel & close orders`

    Args:
      txid: Kraken order identifier (txid), or a user reference (userref) to cancel every order sharing it.
      cl_ord_id: An alphanumeric client order identifier which uniquely identifies an open order for this client.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/trading/cancel-order)
    """
    data = {}
    if txid is not None:
      data['txid'] = txid
    if cl_ord_id is not None:
      data['cl_ord_id'] = cl_ord_id

    return await self.authed_request(
      '/0/private/CancelOrder', data, validator=validate_cancel_order
    )
