from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class PmProTieredCollateralInfo(TypedDict):
  """One collateral rate tier."""

  tierFloor: NotRequired[str]
  """Tier floor."""
  tierCap: NotRequired[str]
  """Tier cap."""
  collateralRate: NotRequired[str]
  """Collateral rate."""
  cum: NotRequired[str]
  """Account equity quick addition number."""


class PmProTieredCollateralRate(TypedDict):
  """Tiered collateral rate for one asset."""

  asset: NotRequired[str]
  """Asset name."""
  collateralInfo: NotRequired[list[PmProTieredCollateralInfo]]
  """Collateral rate tiers."""


class TieredCollateralRate(RpcEndpoint):
  """Portfolio Margin Pro Tiered Collateral Rate"""

  async def tiered_collateral_rate(
    self,
    *,
    validate: bool | None = None,
  ) -> list[PmProTieredCollateralRate]:
    """Portfolio Margin PRO Tiered Collateral Rate.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-derivatives-trading-portfolio-margin-pro/api/rest-api/market-data#portfolio-margin-pro-tiered-collateral-rate)
    """
    _Response = list[PmProTieredCollateralRate]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v2/portfolio/collateralRate',
      validator=_validator,
      validate=validate,
    )
