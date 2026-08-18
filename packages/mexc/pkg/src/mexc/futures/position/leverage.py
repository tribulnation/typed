from typing_extensions import Literal, NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class LeverageItem(TypedDict):
  """Leverage record."""
  positionType: Literal[1, 2]
  """Position side: 1 long, 2 short."""
  level: int
  """Risk level."""
  imr: float
  """Initial margin rate for the leverage risk level."""
  mmr: float
  """Maintenance margin rate for the leverage risk level."""
  leverage: int
  """Configured leverage."""

class LeverageResponse(TypedDict):
  """Get futures position leverage response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[list[LeverageItem]]
  """Leverage records for long and short sides."""

adapter = validator(LeverageResponse)

class Leverage(AuthFuturesMixin):
  async def leverage(self, *, symbol: str, validate: bool | None = None) -> LeverageResponse:
    """Returns leverage and risk-rate details for the signed account on a contract.

    Args:
      symbol: Contract symbol.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-leverage)
    """
    headers = {}
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    r = await self.signed_request('GET', '/api/v1/private/position/leverage', params=params or None, headers=headers)
    return self.envelope_output(r.text, adapter, validate)
