"""`DELETE /api/v3/oco/client-order/{clientOid}` — spot.oco_orders.cancel_by_client_oid."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class CancelOcoOrderResult(TypedDict):
  cancelledOrderIds: list[str]
  """The two leg order ids belonging to the cancelled OCO order."""


_Type = CancelOcoOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class CancelByClientOid(RpcEndpoint):
  """`spot.oco_orders.cancel_by_client_oid` — mixed into `OcoOrders`, the product exposing `spot.oco_orders.cancel_by_client_oid`."""

  async def cancel_by_client_oid(
    self,
    client_oid: str,
    *,
    validate: bool | None = None,
  ) -> CancelOcoOrderResult:
    """Request cancellation of an OCO order by its clientOid. This only submits the cancellation request; the matching engine processes it asynchronously, so confirm the outcome via a lookup or the private WebSocket order push rather than assuming immediate effect.

    Args:
      client_oid: The client-provided order id supplied at placement.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'DELETE',
      f'/api/v3/oco/client-order/{client_oid}',
      validator=adapter,
      validate=validate,
    )
