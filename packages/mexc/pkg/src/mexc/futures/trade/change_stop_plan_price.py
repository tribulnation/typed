from typing_extensions import NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class ChangeStopPlanPriceRequest(TypedDict):
  """Change stop-limit prices for a futures trigger order request body."""
  stopPlanOrderId: int
  """Stop-limit trigger order identifier."""
  stopLossPrice: NotRequired[float]
  """Stop-loss price; at least one stop-loss or take-profit price must be present and greater than 0."""
  takeProfitPrice: NotRequired[float]
  """Take-profit price; at least one stop-loss or take-profit price must be present and greater than 0."""

class ChangeStopPlanPriceResponse(TypedDict):
  """Futures write endpoint response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""

adapter = validator(ChangeStopPlanPriceResponse)

class ChangeStopPlanPrice(AuthFuturesMixin):
  async def change_stop_plan_price(
    self, change_stop_plan_price_request: ChangeStopPlanPriceRequest, *,
    validate: bool | None = None,
  ) -> ChangeStopPlanPriceResponse:
    """Updates stop-loss and/or take-profit prices for a futures stop-limit trigger order.

    Args:
      change_stop_plan_price_request: Request parameter.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#switch-the-stop-limit-price-of-trigger-orders)
    """
    params = {}
    r = await self.signed_post('/api/v1/private/stoporder/change_plan_price', json=change_stop_plan_price_request)
    return self.envelope_output(r.text, adapter, validate)
