"""`GET /api/v1/convert/limit/order/detail` — Get Convert Limit Order Detail."""

from typed_core.validation import validator
from kucoin.types import ConvertLimitOrder
from kucoin.core import RpcEndpoint


_Type = ConvertLimitOrder | None
adapter = validator[_Type](_Type)  # type: ignore


class LimitOrderDetail(RpcEndpoint):
  """`Get Convert Limit Order Detail` — mixed into `Convert`, the product exposing `convert.limit_order_detail`."""

  async def limit_order_detail(
    self,
    *,
    client_order_id: str | None = None,
    order_id: str | None = None,
    validate: bool | None = None,
  ) -> ConvertLimitOrder | None:
    """Get one convert limit order by id. Returns `null` rather than an error when no order matches.

    Args:
      client_order_id: Client-chosen order id from the order's placement. At least one of `clientOrderId`/`orderId` is required by the venue.
      order_id: System-generated order id. At least one of `clientOrderId`/`orderId` is required by the venue.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if client_order_id is not None:
      params['clientOrderId'] = client_order_id
    if order_id is not None:
      params['orderId'] = order_id
    return await self.authed_request(
      'GET',
      '/api/v1/convert/limit/order/detail',
      params=params,
      validator=adapter,
      validate=validate,
    )
