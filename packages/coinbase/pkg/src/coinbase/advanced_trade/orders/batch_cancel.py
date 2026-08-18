from dataclasses import dataclass
from typed_core.validation import validator
from typing_extensions import Literal, TypedDict
from coinbase.core.endpoint.rpc import RpcEndpoint


class CancelOrderResult(TypedDict):
  success: bool
  """Whether the cancel request was submitted successfully."""
  failure_reason: Literal[
    'UNKNOWN_CANCEL_FAILURE_REASON',
    'INVALID_CANCEL_REQUEST',
    'UNKNOWN_CANCEL_ORDER',
    'COMMANDER_REJECTED_CANCEL_ORDER',
    'DUPLICATE_CANCEL_REQUEST',
    'INVALID_CANCEL_PRODUCT_ID',
    'INVALID_CANCEL_FCM_TRADING_SESSION',
    'NOT_ALLOWED_TO_CANCEL',
    'ORDER_IS_FULLY_FILLED',
    'ORDER_IS_BEING_REPLACED',
  ]
  """Why cancellation failed, when `success` is false."""
  order_id: str
  """The order id this result is for."""


class BatchCancelOrdersResponse(TypedDict):
  results: list[CancelOrderResult]
  """One result per requested order id."""


@dataclass(frozen=True, kw_only=True)
class BatchCancel(RpcEndpoint):
  """`POST /api/v3/brokerage/orders/batch_cancel`."""

  async def __call__(self, *, order_ids: list[str]) -> BatchCancelOrdersResponse:
    """Initiate cancellation for one or more orders. Each order's cancel request is attempted independently -- a failure on one order id does not fail the others.

    Args:
      order_ids: The order ids to initiate cancel requests for.

    References:
      - [Official docs](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/orders/cancel-order)
    """
    body: dict = {
      'order_ids': order_ids,
    }
    return await self.authed_request(
      'POST',
      '/api/v3/brokerage/orders/batch_cancel',
      json=body,
      validator=validator(BatchCancelOrdersResponse),
    )
