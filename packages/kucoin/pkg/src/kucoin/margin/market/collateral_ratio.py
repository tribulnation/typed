"""`GET /api/v3/margin/collateralRatio` — Get Margin Collateral Ratio."""

from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class MarginCollateralRatioTier(TypedDict):
  """One collateral-value tier within a ladder."""

  lowerLimit: str
  """Lower bound (inclusive) of this tier's position-value range, in the collateral currency's own units."""
  upperLimit: str
  """Upper bound (exclusive) of this tier's position-value range."""
  collateralRatio: str
  """Collateral ratio applied to position value within this tier -- `1` means full collateral value counts, `0` means none does."""


class MarginCollateralRatioGroup(TypedDict):
  """One collateral-ratio ladder, shared by every currency in `currencyList`."""

  currencyList: list[str]
  """Currencies this ladder applies to."""
  items: list[MarginCollateralRatioTier]
  """Position-value tiers, ascending by range."""


_Type = list[MarginCollateralRatioGroup]
adapter = validator[_Type](_Type)  # type: ignore


class CollateralRatio(RpcEndpoint):
  """`Get Margin Collateral Ratio` — mixed into `Market`, the product exposing `margin.market.collateral_ratio`."""

  async def collateral_ratio(
    self,
    *,
    currency_list: str | None = None,
    validate: bool | None = None,
  ) -> list[MarginCollateralRatioGroup]:
    """Get the collateral-ratio ladder KuCoin applies to margin collateral, grouped by currency and tiered by position value. Public -- no authentication required.

    Args:
      currency_list: Comma-separated currency codes to filter by, e.g. `USDC,USDT`. Omitted returns every currency's ladder.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if currency_list is not None:
      params['currencyList'] = currency_list
    return await self.request(
      'GET',
      '/api/v3/margin/collateralRatio',
      params=params,
      validator=adapter,
      validate=validate,
    )
