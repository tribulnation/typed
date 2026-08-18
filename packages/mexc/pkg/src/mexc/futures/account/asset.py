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

class FuturesAssetResponse(TypedDict):
  """Get single futures asset response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[FuturesAsset]

adapter = validator(FuturesAssetResponse)

class Asset(AuthFuturesMixin):
  async def asset(
    self, currency: str, *,
    validate: bool | None = None,
  ) -> FuturesAssetResponse:
    """Returns balance and equity fields for one currency in the signed futures account.

    Args:
      currency: Currency code to query, for example USDT.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-the-user-39-s-single-currency-asset-information)
    """
    headers = {}
    params = {}
    r = await self.signed_request('GET', '/api/v1/private/account/asset/{currency}'.replace('{currency}', str(currency)), params=params or None, headers=headers)
    return self.envelope_output(r.text, adapter, validate)
