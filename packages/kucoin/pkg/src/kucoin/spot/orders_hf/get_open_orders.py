"""`GET /api/v1/hf/orders/active` — Get Open Orders."""

from typed_core.validation import validator
from kucoin.types import HfOrder
from kucoin.core import RpcEndpoint


_Type = list[HfOrder] | None
adapter = validator[_Type](_Type)  # type: ignore


class GetOpenOrders(RpcEndpoint):
  """`Get Open Orders` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.get_open_orders`."""

  async def get_open_orders(
    self,
    *,
    symbol: str | None = None,
    validate: bool | None = None,
  ) -> list[HfOrder] | None:
    """List every currently open (uncompleted) spot hf order for the authenticated account, sorted descending by last update time. Unpaginated -- see Get Open Orders By Page for a paginated variant.

    Args:
      symbol: Trading pair symbol to filter by. Every open hf order across all symbols is returned when omitted.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    return await self.authed_request(
      'GET',
      '/api/v1/hf/orders/active',
      params=params,
      validator=adapter,
      validate=validate,
    )
