"""`GET /api/v1/earn/kcs-staking/products` — Get KCS-Staking Products."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class KcsStakingProductItem(TypedDict):
  id: str
  """Product id."""
  currency: str
  """Asset being staked -- `KCS`."""
  category: Literal['KCS_STAKING']
  """Product category -- KCS staking is the only one this endpoint offers."""
  type: Literal['TIME', 'DEMAND']
  """Product subtype: `TIME` (fixed-term) or `DEMAND` (flexible). Both observed live."""
  originType: str
  """Undocumented field, absent from KuCoin's own reference -- observed `DEMAND` and `MULTI_TIME_MANUAL` live, neither of which is `type`'s own value on the `TIME` row. Left bare per rule 2: the venue never documents its closed set."""
  precision: int
  """Maximum decimal precision supported."""
  productUpperLimit: str
  """Total subscribable amount across every subscriber."""
  userUpperLimit: str
  """Maximum amount one user may subscribe."""
  userLowerLimit: str
  """Minimum amount one user may subscribe."""
  redeemPeriod: int
  """Redemption waiting period, in days."""
  lockStartTime: int
  """Earliest interest start time, Unix milliseconds."""
  lockEndTime: int | None
  """Product maturity time, Unix milliseconds, or `null` for a `DEMAND` (flexible) product -- confirmed live on both `TIME` (real timestamp) and `DEMAND` (`null`) rows."""
  applyStartTime: int
  """Subscription window start time, Unix milliseconds."""
  applyEndTime: int | None
  """Subscription window end time, Unix milliseconds, or `null` -- `null` on every live row (`TIME` included), undocumented."""
  returnRate: str
  """Annualized rate of return."""
  incomeCurrency: str
  """Currency staking rewards are paid in -- `KCS`."""
  earlyRedeemSupported: Literal[0, 1]
  """Whether early redemption is supported."""
  productRemainAmount: str
  """Remaining subscribable amount."""
  status: Literal['ONGOING', 'PENDING', 'FULL', 'INTERESTING']
  """Subscription status."""
  redeemType: Literal['MANUAL', 'TRANS_DEMAND', 'AUTO']
  """Redemption channel. Every live KCS staking product observed is `MANUAL`."""
  incomeReleaseType: Literal['DAILY', 'AFTER']
  """Whether interest releases daily or only once the product ends."""
  interestDate: int
  """Most recent interest date, Unix milliseconds."""
  duration: int
  """Product duration, in days."""
  newUserOnly: Literal[0, 1]
  """Whether the product is restricted to new users."""


_Type = list[KcsStakingProductItem]
adapter = validator[_Type](_Type)  # type: ignore


class KcsStakingProducts(RpcEndpoint):
  """`Get KCS-Staking Products` — mixed into `Earn`, the product exposing `earn.kcs_staking_products`."""

  async def kcs_staking_products(
    self,
    *,
    currency: str | None = None,
    validate: bool | None = None,
  ) -> list[KcsStakingProductItem]:
    """List the available KCS staking products. Returns an empty list if none are available.

    Args:
      currency: Restrict the response to one currency, e.g. `KCS`. Every currency's products are returned if omitted -- in practice every row is `KCS` regardless.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    return await self.authed_request(
      'GET',
      '/api/v1/earn/kcs-staking/products',
      params=params,
      validator=adapter,
      validate=validate,
    )
