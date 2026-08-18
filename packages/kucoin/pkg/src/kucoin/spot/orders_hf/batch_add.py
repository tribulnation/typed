"""`POST /api/v1/hf/orders/multi` — Batch Add Orders."""

from typing_extensions import NotRequired
from typed_core.validation import TypedDict, validator
from kucoin.types import HfAddOrderLimit, HfAddOrderMarket
from kucoin.core import RpcEndpoint


class HfBatchAddOrderResult(TypedDict):
  """Result of placing a single order from the batch."""

  orderId: str
  """System-generated order id, when placement succeeded."""
  clientOid: str
  """Client-provided order id, echoed back."""
  success: bool
  """Whether this order was placed successfully."""
  failMsg: NotRequired[str]
  """Error message, present only when `success` is `false`."""


class HfBatchAddOrderRequest(TypedDict):
  """Batch order placement request."""

  orderList: list[HfAddOrderLimit | HfAddOrderMarket]
  """Orders to place, up to 20."""


_Type = list[HfBatchAddOrderResult]
adapter = validator[_Type](_Type)  # type: ignore


class BatchAdd(RpcEndpoint):
  """`Batch Add Orders` — mixed into `OrdersHf`, the product exposing `spot.orders_hf.batch_add`."""

  async def batch_add(
    self,
    hf_batch_add_order_request: HfBatchAddOrderRequest,
    *,
    validate: bool | None = None,
  ) -> list[HfBatchAddOrderResult]:
    """Place up to 20 spot hf orders in a single call. Each order in `orderList` is placed independently -- one failing does not prevent the others from being placed.

    Args:
      hf_batch_add_order_request: Orders to place, up to 20.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    return await self.authed_request(
      'POST',
      '/api/v1/hf/orders/multi',
      json=hf_batch_add_order_request,
      validator=adapter,
      validate=validate,
    )
