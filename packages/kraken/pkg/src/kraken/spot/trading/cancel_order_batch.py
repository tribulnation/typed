"""`spot.trading.cancel_order_batch` -- private Spot endpoint."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from ...core.endpoint.rpc import RpcEndpoint


class CancelOrderBatchClientId(TypedDict):
  """One client order identifier to cancel."""

  cl_ord_id: NotRequired[str]
  """An alphanumeric client order identifier which uniquely identifies an open order for this client."""


class CancelOrderBatchTxid(TypedDict):
  """One transaction ID or user reference to cancel."""

  txid: NotRequired[str | int]
  """Open order transaction ID (txid) or user reference (userref)."""


class OrderCancelled(TypedDict):
  """Result of a cancel request."""

  count: NotRequired[int]
  """Number of orders cancelled."""


validate_cancel_order_batch = validator(OrderCancelled)


class CancelOrderBatch(RpcEndpoint):
  """`spot.trading.cancel_order_batch`."""

  async def cancel_order_batch(
    self,
    *,
    orders: list[CancelOrderBatchTxid] | None = None,
    cl_ord_ids: list[CancelOrderBatchClientId] | None = None,
  ) -> OrderCancelled:
    """Cancel multiple open orders by `txid`, `userref` or `cl_ord_id` -- up to 50 unique identifiers/references total across `orders` and `cl_ord_ids`.

    **API Key Permissions Required:** `Orders and trades - Create & modify orders` or `Orders and trades - Cancel & close orders`

    Args:
      orders: Open order transaction IDs or user references to cancel, up to 50 total unique IDs/references across `orders` and `cl_ord_ids`.
      cl_ord_ids: Client order identifiers to cancel, up to 50 total unique IDs/references across `orders` and `cl_ord_ids`.

    References:
      - [Official docs](https://docs.kraken.com/api-reference/trading/cancel-order-batch)
    """
    data = {}
    if orders is not None:
      data['orders'] = orders
    if cl_ord_ids is not None:
      data['cl_ord_ids'] = cl_ord_ids

    return await self.authed_json_request(
      '/0/private/CancelOrderBatch', data, validator=validate_cancel_order_batch
    )
