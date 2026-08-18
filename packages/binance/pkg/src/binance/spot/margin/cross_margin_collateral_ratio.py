from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class MarginCollateralTierBorrowCollateralsItem(TypedDict):
  """One collateral discount-rate tier."""

  minUsdValue: str
  """Minimum USD value of this tier, as a decimal string."""
  maxUsdValue: NotRequired[str]
  """Maximum USD value of this tier, as a decimal string. Absent for the top, unbounded tier."""
  discountRate: str
  """Collateral discount rate applied within this tier, as a decimal string."""


class MarginCollateralTierCollateralsItem(TypedDict):
  """One collateral discount-rate tier."""

  minUsdValue: str
  """Minimum USD value of this tier, as a decimal string."""
  maxUsdValue: NotRequired[str]
  """Maximum USD value of this tier, as a decimal string. Absent for the top, unbounded tier -- confirmed live: this account's real response had exactly one tier, with no `maxUsdValue` at all."""
  discountRate: str
  """Collateral discount rate applied within this tier, as a decimal string."""


class MarginCollateralTierWithdrawCollateralsItem(TypedDict):
  """One collateral discount-rate tier."""

  minUsdValue: str
  """Minimum USD value of this tier, as a decimal string."""
  maxUsdValue: NotRequired[str]
  """Maximum USD value of this tier, as a decimal string. Absent for the top, unbounded tier."""
  discountRate: str
  """Collateral discount rate applied within this tier, as a decimal string."""


class MarginCollateralRatio(TypedDict):
  """Collateral discount-rate tiers for a group of assets."""

  collaterals: list[MarginCollateralTierCollateralsItem]
  """General discount-rate tiers, by USD value range."""
  withdrawCollaterals: list[MarginCollateralTierWithdrawCollateralsItem]
  """Discount-rate tiers applied specifically for withdrawal eligibility checks, by USD value range. Missing from the docs-only pass's schema entirely -- added from live evidence."""
  borrowCollaterals: list[MarginCollateralTierBorrowCollateralsItem]
  """Discount-rate tiers applied specifically for borrow eligibility checks, by USD value range. Missing from the docs-only pass's schema entirely -- added from live evidence."""
  assetNames: list[str]
  """Assets these collateral tiers apply to."""


class CrossMarginCollateralRatio(RpcEndpoint):
  """Cross Margin Collateral Ratio"""

  async def cross_margin_collateral_ratio(
    self,
    *,
    validate: bool | None = None,
  ) -> list[MarginCollateralRatio]:
    """Query the collateral discount-rate tiers applied to cross margin assets when used as collateral, grouped by USD value range.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-margin-trading/api/rest-api/market-data#cross-margin-collateral-ratio)
    """
    _Response = list[MarginCollateralRatio]
    _validator = validator[_Response](_Response)
    return await self.request(
      'GET',
      '/sapi/v1/margin/crossMarginCollateralRatio',
      validator=_validator,
      validate=validate,
    )
