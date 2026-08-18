from typing_extensions import NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class CancelAllPlanRequest(TypedDict):
  """Cancel all futures trigger orders request body."""
  symbol: NotRequired[str]
  """Contract symbol to scope cancellation; omit to cancel all trigger orders."""

class CancelAllPlanResponse(TypedDict):
  """Futures write endpoint response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""

adapter = validator(CancelAllPlanResponse)

class CancelAllPlan(AuthFuturesMixin):
  async def cancel_all_plan(
    self, cancel_all_plan_request: CancelAllPlanRequest, *,
    validate: bool | None = None,
  ) -> CancelAllPlanResponse:
    """Cancels all uncompleted trigger orders, optionally scoped to a contract symbol.

    Args:
      cancel_all_plan_request: Request parameter.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#cancel-all-trigger-orders-under-maintenance)
    """
    params = {}
    r = await self.signed_post('/api/v1/private/planorder/cancel_all', json=cancel_all_plan_request)
    return self.envelope_output(r.text, adapter, validate)
