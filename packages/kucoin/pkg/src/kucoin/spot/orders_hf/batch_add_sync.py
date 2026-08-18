"""`POST /api/v1/hf/orders/multi/sync` — Batch Add Orders Sync."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp
from kucoin.types import HfAddOrderLimit, HfAddOrderMarket


class HfBatchAddOrderSyncResult(TypedDict):
  """Result of placing a single order from the batch, including fill state."""

  orderId: str
  """System-generated order id, when placement succeeded."""
  clientOid: str
  """Client-provided order id, echoed back."""
  orderTime: NotRequired[Timestamp]
  """Order placement time."""
  originSize: NotRequired[str]
  """Original order quantity."""
  dealSize: NotRequired[str]
  """Quantity filled by the time the call returned."""
  remainSize: NotRequired[str]
  """Quantity not yet filled."""
  canceledSize: NotRequired[str]
  """Quantity cancelled, e.g. by IOC/FOK expiry."""
  status: NotRequired[str]
  """Order status at the time the call returned, e.g. `open`. Left as a plain string since KuCoin does not publish the closed set."""
  matchTime: NotRequired[Timestamp]
  """Time the matching engine finished processing the order."""
  success: bool
  """Whether this order was placed successfully."""
  failMsg: NotRequired[str]
  """Error message, present only when `success` is `false`."""


class HfBatchAddOrderSyncRequest(TypedDict):
  """Batch order placement request."""

  orderList: list[HfAddOrderLimit | HfAddOrderMarket]
  """Orders to place, up to 20."""


_Type = list[HfBatchAddOrderSyncResult]
adapter = validator[_Type](_Type)  # type: ignore


class BatchAddSync(RpcEndpoint):
  """`Batch Add Orders Sync` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.batch_add_sync`."""

  async def batch_add_sync(
    self,
    hf_batch_add_order_sync_request: HfBatchAddOrderSyncRequest,
    *,
    validate: bool | None = None,
  ) -> list[HfBatchAddOrderSyncResult]:
    """Place up to 20 spot hf orders in a single call and wait for each order's matching-engine result before responding, rather than Batch Add's fire-and-forget acknowledgement.

    Args:
      hf_batch_add_order_sync_request: Orders to place, up to 20.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/hf/orders/multi/sync',
      json=hf_batch_add_order_sync_request,
      validator=adapter,
      validate=validate,
    )
