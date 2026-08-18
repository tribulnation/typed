from typing_extensions import NotRequired, TypedDict
from mexc.core import Timestamp, validator
from mexc.futures.core import FuturesMixin

class RiskReverseItem(TypedDict):
  """Risk fund balance record."""
  symbol: str
  """Contract symbol."""
  currency: str
  """Risk fund currency."""
  available: float
  """Available risk fund balance."""
  timestamp: Timestamp
  """System timestamp in milliseconds."""

class RiskReverseResponse(TypedDict):
  """Risk fund balance envelope"""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[list[RiskReverseItem]]
  """Risk fund balance records."""

adapter = validator(RiskReverseResponse)

class RiskReverse(FuturesMixin):
  async def risk_reverse(self, *, validate: bool | None = None) -> RiskReverseResponse:
    """Return all contract risk fund balances.

    Args:
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-all-contract-risk-fund-balance)
    """
    params = {}
    r = await self.request('GET', '/api/v1/contract/risk_reverse')
    return self.envelope_output(r.text, adapter, validate)
