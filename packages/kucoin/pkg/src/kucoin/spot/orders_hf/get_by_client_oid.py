"""`GET /api/v1/hf/orders/client-order/{clientOid}` — Get Order By ClientOid."""

from typed_core.validation import validator
from kucoin.types import HfOrder
from kucoin.core import RpcEndpoint


_Type = HfOrder
adapter = validator[_Type](_Type)  # type: ignore


class GetByClientOid(RpcEndpoint):
  """`Get Order By ClientOid` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.get_by_client_oid`."""

  async def get_by_client_oid(
    self,
    client_oid: str,
    *,
    symbol: str,
    validate: bool | None = None,
  ) -> HfOrder:
    """Get a single spot hf order's full detail by its client-provided order id. Cancelled orders are queryable for 2 days after cancellation, filled orders for 7 days after filling.

    Args:
      client_oid: Client-provided id of the order to look up.
      symbol: Trading pair symbol the order belongs to.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
    }
    return await self.authed_request(
      'GET',
      f'/api/v1/hf/orders/client-order/{client_oid}',
      params=params,
      validator=adapter,
      validate=validate,
    )
