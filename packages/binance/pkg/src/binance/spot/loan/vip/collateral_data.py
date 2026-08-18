from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class VipLoanCollateralAsset(TypedDict):
  """One collateral coin's tiered collateral ratios. Each numbered tier applies to a successive slice of the collateral's haircut-adjusted value, most favorable tier first."""

  collateralCoin: NotRequired[str]
  """Collateral coin."""
  _1stCollateralRatio: NotRequired[str]
  """Collateral ratio applied to the first value tier, as a decimal string."""
  _1stCollateralRange: NotRequired[str]
  """Value range of the first collateral tier."""
  _2ndCollateralRatio: NotRequired[str]
  """Collateral ratio applied to the second value tier, as a decimal string."""
  _2ndCollateralRange: NotRequired[str]
  """Value range of the second collateral tier."""
  _3rdCollateralRatio: NotRequired[str]
  """Collateral ratio applied to the third value tier, as a decimal string."""
  _3rdCollateralRange: NotRequired[str]
  """Value range of the third collateral tier."""
  _4thCollateralRatio: NotRequired[str]
  """Collateral ratio applied to the fourth value tier, as a decimal string."""
  _4thCollateralRange: NotRequired[str]
  """Value range of the fourth collateral tier."""


class VipLoanCollateralAssetDataPage(TypedDict):
  """Collateral asset data. Not observed to accept page parameters despite the `rows`/`total` shape -- see this endpoint's notes."""

  rows: NotRequired[list[VipLoanCollateralAsset]]
  """Matching collateral assets."""
  total: NotRequired[int]
  """Total number of matching collateral assets."""


class CollateralData(RpcEndpoint):
  """Get VIP loan collateral asset data, including the tiered collateral ratios applied above successive haircut-adjusted value ranges."""

  async def collateral_data(
    self,
    *,
    collateral_coin: str | None = None,
    validate: bool | None = None,
  ) -> VipLoanCollateralAssetDataPage:
    """Get VIP loan collateral asset data, including the tiered collateral ratios applied above successive haircut-adjusted value ranges.

    Args:
      collateral_coin: Restrict results to one collateral coin.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-vip-loan/api/rest-api/market-data#get-collateral-asset-data)
    """
    params = {}
    if collateral_coin is not None:
      params['collateralCoin'] = collateral_coin
    _Response = VipLoanCollateralAssetDataPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/loan/vip/collateral/data',
      params=params,
      validator=_validator,
      validate=validate,
    )
