"""`GET /api/v3/hf/margin/oco-order/clientOid` — Get OCO Order By ClientOid."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp


class MarginOcoOrderSummary(TypedDict):
  """Lightweight OCO order summary, with no leg detail."""

  orderId: str
  """OCO order group id."""
  symbol: str
  """Trading pair."""
  clientOid: str
  """Client-provided order id, as supplied at placement."""
  orderTime: Timestamp
  """Time the OCO order was placed."""
  status: Literal['NEW', 'DONE', 'TRIGGERED', 'CANCELLED']
  """OCO order group status. Carried over from Spot's confirmed `OcoOrderSummary.status` enum -- not independently confirmed by this endpoint's own docs prose."""


_Type = MarginOcoOrderSummary | None
adapter = validator[_Type](_Type)  # type: ignore


class GetByClientOid(RpcEndpoint):
  """`Get OCO Order By ClientOid` — mixed into `OcoOrders`, the product exposing `margin.oco_orders.get_by_client_oid`."""

  async def get_by_client_oid(
    self,
    *,
    client_oid: str,
    validate: bool | None = None,
  ) -> MarginOcoOrderSummary | None:
    """Get a lightweight margin OCO order summary (no leg detail) by its clientOid, or `null` when no such order exists for this account. Same lightweight shape as Get OCO Order By OrderId.

    Args:
      client_oid: The client-provided order id supplied at placement.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'clientOid': client_oid,
    }
    return await self.authed_request(
      'GET',
      '/api/v3/hf/margin/oco-order/clientOid',
      params=params,
      validator=adapter,
      validate=validate,
    )
