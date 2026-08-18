"""`POST /api/v1/hf/orders/test` — Add Order Test."""

from typed_core.validation import TypedDict, validator
from kucoin.types import HfAddOrderLimit, HfAddOrderMarket
from kucoin.core import RpcEndpoint


class HfAddOrderResult(TypedDict):
  """Identifiers that would have been assigned had the order actually been placed."""

  orderId: str
  """Placeholder order id -- no real order exists behind it."""
  clientOid: str
  """Client-provided order id, echoed back."""


_Type = HfAddOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class AddTest(RpcEndpoint):
  """`Add Order Test` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.add_test`."""

  async def add_test(
    self,
    body: HfAddOrderLimit | HfAddOrderMarket,
    *,
    validate: bool | None = None,
  ) -> HfAddOrderResult:
    """Validate a spot hf order placement request against the same checks Add applies -- symbol, permissions, size/price limits -- without ever entering the matching engine. Used to test order-placement integration safely.

    Args:
      body: Order placement parameters, identical to Add.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/hf/orders/test',
      json=body,
      validator=adapter,
      validate=validate,
    )
