"""`DELETE /api/v1/hf/orders/sync/{orderId}` — Cancel Order By OrderId Sync."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class HfCancelOrderSyncResult(TypedDict):
  """Order state confirmed cancelled."""

  orderId: str
  """System-generated id of the cancelled order."""
  originSize: str
  """Original order quantity."""
  dealSize: str
  """Quantity that had been filled before cancellation."""
  remainSize: str
  """Quantity that was still unfilled."""
  canceledSize: str
  """Quantity cancelled by this call."""
  status: str
  """Final order status, e.g. `done`. Left as a plain string since KuCoin does not publish the closed set."""


_Type = HfCancelOrderSyncResult
adapter = validator[_Type](_Type)  # type: ignore


class CancelByOrderIdSync(RpcEndpoint):
  """`Cancel Order By OrderId Sync` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.cancel_by_order_id_sync`."""

  async def cancel_by_order_id_sync(
    self,
    order_id: str,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> HfCancelOrderSyncResult:
    """Cancel a single spot hf order by its system-generated order id and wait for the cancellation to complete before responding, rather than Cancel by OrderId's fire-and-forget acknowledgement.

    Args:
      order_id: System-generated id of the order to cancel.
      symbol: Trading pair symbol the order belongs to.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.authed_request(
      'DELETE',
      f'/api/v1/hf/orders/sync/{order_id}',
      params=params,
      validator=adapter,
      validate=validate,
    )
