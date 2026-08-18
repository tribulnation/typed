from typing_extensions import Literal, NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class PlacePlanRequest(TypedDict):
  """Place futures trigger order request body."""
  symbol: str
  """Contract symbol."""
  price: NotRequired[float]
  """Execution price; may be omitted for market-price execution."""
  vol: float
  """Order volume in contracts."""
  leverage: NotRequired[int]
  """Leverage, required for isolated margin according to docs."""
  side: Literal[1, 2, 3, 4]
  """Order direction: 1 open long, 2 close short, 3 open short, 4 close long."""
  openType: Literal[1, 2]
  """Margin mode: 1 isolated, 2 cross."""
  triggerPrice: float
  """Trigger price."""
  triggerType: Literal[1, 2]
  """Trigger condition: 1 greater than or equal, 2 less than or equal."""
  executeCycle: Literal[1, 2]
  """Execution cycle: 1 for 24 hours, 2 for 7 days."""
  orderType: Literal[1, 2, 3, 4, 5]
  """Execution order type: 1 limit, 2 post-only maker, 3 IOC, 4 FOK, 5 market."""
  trend: Literal[1, 2, 3]
  """Trigger price source: 1 latest price, 2 fair price, 3 index price."""

class PlacePlanResponse(TypedDict):
  """Futures write endpoint response envelope with created order id."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[int | str | None]
  """Order identifier returned when creation succeeds; null or absent when creation fails."""

adapter = validator(PlacePlanResponse)

class PlacePlan(AuthFuturesMixin):
  async def place_plan(
    self, place_plan_request: PlacePlanRequest, *,
    validate: bool | None = None,
  ) -> PlacePlanResponse:
    """Places a futures trigger order with trigger price, trigger direction, execution cycle, and execution order type.

    Args:
      place_plan_request: Request parameter.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#trigger-order-under-maintenance)
    """
    params = {}
    r = await self.signed_post('/api/v1/private/planorder/place', json=place_plan_request)
    return self.envelope_output(r.text, adapter, validate)
