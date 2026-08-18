"""`DELETE /api/v1/hf/orders/sync/client-order/{clientOid}` — Cancel Order By ClientOid Sync."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class HfCancelOrderByClientOidSyncResult(TypedDict):
  """Order state confirmed cancelled."""

  clientOid: str
  """Client-provided id of the cancelled order."""
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


_Type = HfCancelOrderByClientOidSyncResult
adapter = validator[_Type](_Type)  # type: ignore


class CancelByClientOidSync(RpcEndpoint):
  """`Cancel Order By ClientOid Sync` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.cancel_by_client_oid_sync`."""

  async def cancel_by_client_oid_sync(
    self,
    client_oid: str,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> HfCancelOrderByClientOidSyncResult:
    """Cancel a single spot hf order by its client-provided order id and wait for the cancellation to complete before responding, rather than Cancel by ClientOid's fire-and-forget acknowledgement.

    Args:
      client_oid: Client-provided id of the order to cancel.
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
      f'/api/v1/hf/orders/sync/client-order/{client_oid}',
      params=params,
      validator=adapter,
      validate=validate,
    )
