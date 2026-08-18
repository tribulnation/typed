from typing_extensions import NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class CancelStopItem(TypedDict):
  """Single stop-limit trigger cancellation request."""
  stopPlanOrderId: int
  """Stop-limit trigger order identifier."""

class CancelStopResponse(TypedDict):
  """Futures write endpoint response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""

adapter = validator(CancelStopResponse)

class CancelStop(AuthFuturesMixin):
  async def cancel_stop(
    self, list_cancel_stop_item: list[CancelStopItem], *,
    validate: bool | None = None,
  ) -> CancelStopResponse:
    """Cancels up to 50 futures stop-limit trigger orders by stop-plan order id.

    Args:
      list_cancel_stop_item: Request parameter.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#cancel-the-stop-limit-trigger-order-under-maintenance)
    """
    params = {}
    r = await self.signed_post('/api/v1/private/stoporder/cancel', json=list_cancel_stop_item)
    return self.envelope_output(r.text, adapter, validate)
