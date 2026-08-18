"""`POST /api/v1/hf/orders/sync` — Add Order Sync."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp
from kucoin.types import HfAddOrderLimit, HfAddOrderMarket


class HfAddOrderSyncResult(TypedDict):
  """Order result, including fill state, since the call waits for the matching engine."""

  orderId: str
  """System-generated order id."""
  clientOid: str
  """Client-provided order id, echoed back."""
  orderTime: Timestamp
  """Order placement time."""
  originSize: str
  """Original order quantity."""
  dealSize: str
  """Quantity filled by the time the call returned."""
  remainSize: str
  """Quantity not yet filled."""
  canceledSize: str
  """Quantity cancelled, e.g. by IOC/FOK expiry."""
  status: str
  """Order status at the time the call returned, e.g. `open`. KuCoin's docs give this example without stating the closed set, so left as a plain string rather than a guessed enum."""
  matchTime: Timestamp
  """Time the matching engine finished processing the order."""


_Type = HfAddOrderSyncResult
adapter = validator[_Type](_Type)  # type: ignore


class AddSync(RpcEndpoint):
  """`Add Order Sync` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.add_sync`."""

  async def add_sync(
    self,
    body: HfAddOrderLimit | HfAddOrderMarket,
    *,
    validate: bool | None = None,
  ) -> HfAddOrderSyncResult:
    """Place a spot hf limit or market order and wait for the matching engine's result before responding, rather than Add's fire-and-forget acknowledgement.

    Args:
      body: Order placement parameters, identical to Add.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/hf/orders/sync',
      json=body,
      validator=adapter,
      validate=validate,
    )
