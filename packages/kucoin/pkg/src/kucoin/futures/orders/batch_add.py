"""`POST /api/v1/orders/multi` — Batch Add Orders."""

from typed_core.validation import TypedDict, validator
from kucoin.types import FuturesAddOrderLimit, FuturesAddOrderMarket
from kucoin.core import RpcEndpoint


class FuturesBatchAddOrderResult(TypedDict):
  """One order's placement result -- success or failure."""

  orderId: str
  """System-generated order id."""
  clientOid: str
  """Client-provided order id, echoed back."""
  symbol: str
  """Contract symbol this order was for."""
  code: str
  """This item's own result code -- `200000` on success, an error code otherwise. Distinct from the outer envelope code, which is unwrapped by the core before this schema applies."""
  msg: str
  """This item's own result message."""


_Type = list[FuturesBatchAddOrderResult]
adapter = validator[_Type](_Type)  # type: ignore


class BatchAdd(RpcEndpoint):
  """`Batch Add Orders` — mixed into `Orders`, the product exposing `futures.orders.batch_add`."""

  async def batch_add(
    self,
    body: list[FuturesAddOrderLimit | FuturesAddOrderMarket],
    *,
    validate: bool | None = None,
  ) -> list[FuturesBatchAddOrderResult]:
    """Place up to 20 limit or market orders in a single request. Each item is validated and placed independently -- one order failing does not prevent the others from being placed.

    Args:
      body: Up to 20 order placement parameter sets.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/orders/multi',
      json=body,
      validator=adapter,
      validate=validate,
    )
