"""`POST /api/v3/hf/margin/order/test` — Add Order Test."""

from typed_core.validation import TypedDict, validator
from kucoin.types import HfMarginAddOrderLimit, HfMarginAddOrderMarket
from kucoin.core import RpcEndpoint


class HfMarginAddOrderResult(TypedDict):
  """Identifiers that would have been assigned had the order actually been placed, plus loan details it would have carried under `autoBorrow`."""

  orderId: str
  """Placeholder order id -- no real order exists behind it."""
  clientOid: str
  """Client-provided order id, echoed back."""
  loanApplyId: str | None
  """Placeholder loan application id under `autoBorrow`, or `null` when the request did not set it."""
  borrowSize: str | None
  """Placeholder borrowed amount under `autoBorrow`, or `null` when the request did not set it."""


_Type = HfMarginAddOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class AddTest(RpcEndpoint):
  """`Add Order Test` — mixed into `OrdersHf`, the product exposing `margin.orders_hf.add_test`."""

  async def add_test(
    self,
    body: HfMarginAddOrderLimit | HfMarginAddOrderMarket,
    *,
    validate: bool | None = None,
  ) -> HfMarginAddOrderResult:
    """Validate a margin hf order placement request against the same checks Add applies -- signature, symbol, parameters -- without ever entering the matching engine. An order placed through this endpoint cannot be queried afterwards by any other endpoint.

    Args:
      body: Order placement parameters, identical to Add.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/hf/margin/order/test',
      json=body,
      validator=adapter,
      validate=validate,
    )
