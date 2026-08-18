from typing_extensions import NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin
from mexc.core import validator

class FuturesAsset(TypedDict):
  """Futures asset balance."""
  currency: str
  """Asset currency code."""
  positionMargin: float
  """Margin currently assigned to positions."""
  frozenBalance: float
  """Balance frozen by orders or positions."""
  availableBalance: float
  """Balance available for trading or transfer."""
  cashBalance: float
  """Drawable cash balance."""
  equity: float
  """Total account equity for the currency."""
  unrealized: float
  """Unrealized profit and loss."""
  bonus: NotRequired[float]
  """Bonus balance when present."""

class FuturesAssetsResponse(TypedDict):
  """Get all futures account assets response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[list[FuturesAsset]]
  """All futures asset balances."""

adapter = validator(FuturesAssetsResponse)

class Assets(AuthFuturesMixin):
  async def assets(self, *, validate: bool | None = None) -> FuturesAssetsResponse:
    """Returns all currency balances for the signed futures account.

    Args:
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-all-informations-of-user-39-s-asset)
    """
    headers = {}
    params = {}
    r = await self.signed_request('GET', '/api/v1/private/account/assets', params=params or None, headers=headers)
    return self.envelope_output(r.text, adapter, validate)
