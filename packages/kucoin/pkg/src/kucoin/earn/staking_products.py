"""`GET /api/v1/earn/staking/products` — Get Staking Products."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class StakingProductItem(TypedDict):
  id: str
  """Product id."""
  currency: str
  """Asset being staked, e.g. `ADA`."""
  category: Literal['STAKING']
  """Product category -- staking is the only one this endpoint offers."""
  type: Literal['DEMAND']
  """Product subtype. Every live staking product observed is `DEMAND` (flexible) -- `TIME` (fixed-term) is a sibling products' value, not confirmed here."""
  originType: str
  """Undocumented field, absent from KuCoin's own reference -- observed identical to `type` (`DEMAND`) on every live staking product. Left bare per rule 2: the venue never documents its closed set."""
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
  """Product maturity time, Unix milliseconds, or `null` -- `null` on every live (`DEMAND`) row, matching `earn.savings_products`."""
  applyStartTime: int
  """Subscription window start time, Unix milliseconds."""
  applyEndTime: int | None
  """Subscription window end time, Unix milliseconds, or `null` -- `null` on every live row, same drift as `lockEndTime`."""
  returnRate: str
  """Annualized rate of return."""
  incomeCurrency: str
  """Currency staking rewards are paid in."""
  earlyRedeemSupported: Literal[0, 1]
  """Whether early redemption is supported."""
  productRemainAmount: str
  """Remaining subscribable amount."""
  status: Literal['ONGOING', 'PENDING', 'FULL', 'INTERESTING']
  """Subscription status."""
  redeemType: Literal['MANUAL', 'TRANS_DEMAND', 'AUTO']
  """Redemption channel. Every live staking product observed is `MANUAL`."""
  incomeReleaseType: Literal['DAILY', 'AFTER']
  """Whether interest releases daily or only once the product ends."""
  interestDate: int
  """Most recent interest date, Unix milliseconds."""
  duration: int
  """Product duration, in days."""
  newUserOnly: Literal[0, 1]
  """Whether the product is restricted to new users."""


_Type = list[StakingProductItem]
adapter = validator[_Type](_Type)  # type: ignore


class StakingProducts(RpcEndpoint):
  """`Get Staking Products` — mixed into `Earn`, the product exposing `earn.staking_products`."""

  async def staking_products(
    self,
    *,
    currency: str | None = None,
    validate: bool | None = None,
  ) -> list[StakingProductItem]:
    """List the general (non-KCS, non-ETH) staking products currently on offer. Returns an empty list if none are available.

    Args:
      currency: Restrict the response to one currency, e.g. `ADA`. Every currency's products are returned if omitted.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    return await self.authed_request(
      'GET',
      '/api/v1/earn/staking/products',
      params=params,
      validator=adapter,
      validate=validate,
    )
