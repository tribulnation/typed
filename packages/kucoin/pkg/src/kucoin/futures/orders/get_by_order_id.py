"""`GET /api/v1/orders/{order-id}` — Get Order By OrderId."""

from typed_core.validation import validator
from kucoin.types import FuturesOrder
from kucoin.core import RpcEndpoint


_Type = FuturesOrder
adapter = validator[_Type](_Type)  # type: ignore


class GetByOrderId(RpcEndpoint):
  """`Get Order By OrderId` — mixed into `Orders`, the product exposing `futures.orders.get_by_order_id`."""

  async def get_by_order_id(
    self,
    order_id: str,
    *,
    validate: bool | None = None,
  ) -> FuturesOrder:
    """Get a single futures order (including a stop order) by its system-generated order id. Historical (filled/cancelled) orders are only queryable within a limited time window.

    Args:
      order_id: System-generated id of the order to look up. KuCoin's own path template spells this segment `order-id` (hyphenated), unlike every other order endpoint here which uses `orderId` -- confirmed against the official SDK spec's path key, not a transcription choice.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'GET',
      f'/api/v1/orders/{order_id}',
      validator=adapter,
      validate=validate,
    )
