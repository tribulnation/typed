"""`DELETE /api/v1/hf/orders/client-order/{clientOid}` — Cancel Order By ClientOid."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class HfCancelOrderByClientOidResult(TypedDict):
  """Identifier of the order the cancellation request was accepted for."""

  clientOid: str
  """Client-provided id of the order being cancelled."""


_Type = HfCancelOrderByClientOidResult
adapter = validator[_Type](_Type)  # type: ignore


class CancelByClientOid(RpcEndpoint):
  """`Cancel Order By ClientOid` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.cancel_by_client_oid`."""

  async def cancel_by_client_oid(
    self,
    client_oid: str,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> HfCancelOrderByClientOidResult:
    """Cancel a single spot hf order by its client-provided order id. Sends a cancellation request only -- confirm via Get by ClientOid or the private order WebSocket feed.

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
      f'/api/v1/hf/orders/client-order/{client_oid}',
      params=params,
      validator=adapter,
      validate=validate,
    )
