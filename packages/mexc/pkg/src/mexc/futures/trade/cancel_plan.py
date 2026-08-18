from typing_extensions import NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class CancelPlanItem(TypedDict):
  """Single trigger order cancellation request."""
  symbol: str
  """Contract symbol."""
  orderId: str
  """Trigger order identifier."""

class CancelPlanResponse(TypedDict):
  """Futures write endpoint response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""

adapter = validator(CancelPlanResponse)

class CancelPlan(AuthFuturesMixin):
  async def cancel_plan(
    self, list_cancel_plan_item: list[CancelPlanItem], *,
    validate: bool | None = None,
  ) -> CancelPlanResponse:
    """Cancels up to 50 futures trigger orders.

    Args:
      list_cancel_plan_item: Request parameter.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#cancel-the-trigger-order-under-maintenance)
    """
    params = {}
    r = await self.signed_post('/api/v1/private/planorder/cancel', json=list_cancel_plan_item)
    return self.envelope_output(r.text, adapter, validate)
