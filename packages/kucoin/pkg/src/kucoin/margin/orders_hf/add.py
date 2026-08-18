"""`POST /api/v3/hf/margin/order` — Add Order."""

from typed_core.validation import TypedDict, validator
from kucoin.types import HfMarginAddOrderLimit, HfMarginAddOrderMarket
from kucoin.core import RpcEndpoint


class HfMarginAddOrderResult(TypedDict):
  """Identifiers of the newly placed order, plus loan details when it auto-borrowed."""

  orderId: str
  """System-generated order id."""
  clientOid: str
  """Client-provided order id, echoed back."""
  loanApplyId: str | None
  """Id of the loan application this order triggered under `autoBorrow`, or `null` when the order did not borrow."""
  borrowSize: str | None
  """Amount borrowed under `autoBorrow`, or `null` when the order did not borrow."""


_Type = HfMarginAddOrderResult
adapter = validator[_Type](_Type)  # type: ignore


class Add(RpcEndpoint):
  """`Add Order` — mixed into `OrdersHf`, the product exposing `margin.orders_hf.add`."""

  async def add(
    self,
    body: HfMarginAddOrderLimit | HfMarginAddOrderMarket,
    *,
    validate: bool | None = None,
  ) -> HfMarginAddOrderResult:
    """Place a margin high-frequency (hf) limit or market order against the cross-margin or isolated-margin trading system. Funds are held for the order's duration once placed; up to 2000 active orders per account and 200 per trading pair.

    Args:
      body: Order placement parameters.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v3/hf/margin/order',
      json=body,
      validator=adapter,
      validate=validate,
    )
