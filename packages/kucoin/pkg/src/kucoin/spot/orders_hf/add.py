"""`POST /api/v1/hf/orders` — Add Order."""

from typed_core.validation import TypedDict, validator
from kucoin.types import HfAddOrderLimit, HfAddOrderMarket
from kucoin.core import RpcEndpoint


class HfAddOrderResult(TypedDict):
  """Identifiers of the newly placed order."""

  orderId: str
  """System-generated order id."""
  clientOid: str
  """Client-provided order id, echoed back."""


_Type = HfAddOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class Add(RpcEndpoint):
  """`Add Order` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.add`."""

  async def add(
    self,
    body: HfAddOrderLimit | HfAddOrderMarket,
    *,
    validate: bool | None = None,
  ) -> HfAddOrderResult:
    """Place a spot high-frequency (hf) limit or market order. hf orders match through a dedicated matching engine with lower latency than the plain spot order book.

    Args:
      body: Order placement parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/hf/orders',
      json=body,
      validator=adapter,
      validate=validate,
    )
