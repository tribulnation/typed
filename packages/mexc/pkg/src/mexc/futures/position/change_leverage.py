from typing_extensions import Literal, NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class ChangeLeverageRequest(TypedDict):
  """Change futures leverage request body."""
  positionId: NotRequired[int]
  """Existing position identifier when changing leverage for a held position."""
  leverage: int
  """Target leverage."""
  openType: NotRequired[Literal[1, 2]]
  """Required when there is no position; 1 isolated, 2 cross."""
  symbol: NotRequired[str]
  """Required when there is no position; contract symbol."""
  positionType: NotRequired[Literal[1, 2]]
  """Required when there is no position; 1 long, 2 short."""

class ChangeLeverageResponse(TypedDict):
  """Futures write endpoint response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""

adapter = validator(ChangeLeverageResponse)

class ChangeLeverage(AuthFuturesMixin):
  async def change_leverage(
    self, change_leverage_request: ChangeLeverageRequest, *,
    validate: bool | None = None,
  ) -> ChangeLeverageResponse:
    """Changes leverage either for an existing position or for a symbol/open-type/side when no position exists.

    Args:
      change_leverage_request: Request parameter.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#switch-leverage)
    """
    params = {}
    r = await self.signed_post('/api/v1/private/position/change_leverage', json=change_leverage_request)
    return self.envelope_output(r.text, adapter, validate)
