"""`GET /api/v1/earn/saving/products` — Get Savings Products."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp


class SavingsProduct(TypedDict):
  """One flexible or fixed-term savings product on offer."""

  id: str
  """Product ID."""
  currency: str
  """Product currency, for example `BTC`."""
  category: Literal['DEMAND']
  """Product category — savings is the only one currently offered."""
  type: Literal['TIME', 'DEMAND']
  """Product subtype: `TIME` (fixed-term) or `DEMAND` (flexible)."""
  originType: str
  """Undocumented field, absent from KuCoin's own reference -- observed identical to
  `type` on every live savings product (2026-08-08), but left untyped since the venue
  never states it's the same closed set."""
  precision: int
  """Maximum decimal precision supported."""
  productUpperLimit: str
  """Total subscription amount across every subscriber."""
  userUpperLimit: str
  """Max. amount one user may subscribe."""
  userLowerLimit: str
  """Min. amount one user may subscribe."""
  redeemPeriod: int
  """Redemption waiting period, in days."""
  lockStartTime: Timestamp
  """Earliest interest start time."""
  lockEndTime: Timestamp | None
  """Product maturity time, `None` for a `DEMAND` (flexible, no maturity) product --
  confirmed live: every `DEMAND` row returns `null` here."""
  applyStartTime: Timestamp
  """Subscription window start time."""
  applyEndTime: Timestamp | None
  """Subscription window end time, `None` for a `DEMAND` product -- same drift as
  `lockEndTime`."""
  returnRate: str
  """Annualized rate of return, for example `"0.035"` for 3.5%."""
  incomeCurrency: str
  """Currency interest is paid in."""
  earlyRedeemSupported: Literal[0, 1]
  """Whether a fixed-term product supports early redemption."""
  productRemainAmount: str
  """Remaining subscribable amount."""
  status: Literal['ONGOING', 'PENDING', 'FULL', 'INTERESTING']
  """Subscription status."""
  redeemType: Literal['MANUAL', 'TRANS_DEMAND', 'AUTO']
  """Redemption channel."""
  incomeReleaseType: Literal['DAILY', 'AFTER']
  """Whether interest releases daily or only once the product ends."""
  interestDate: Timestamp
  """Most recent interest date."""
  duration: int
  """Product duration, in days."""
  newUserOnly: Literal[0, 1]
  """Whether the product is restricted to new users."""


adapter = validator(list[SavingsProduct])


class SavingsProducts(RpcEndpoint):
  """`Get Savings Products` — mixed into `Earn`, the product exposing
  `earn.savings_products`."""

  async def savings_products(
    self,
    *,
    currency: str | None = None,
    validate: bool | None = None,
  ) -> list[SavingsProduct]:
    """List flexible and fixed-term savings products currently on offer.

    Args:
      currency: Restrict the response to one currency, for example `USDT`. Omit for every
        currency.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {'currency': currency} if currency is not None else None
    return await self.authed_request(
      'GET',
      '/api/v1/earn/saving/products',
      params=params,
      validator=adapter,
      validate=validate,
    )
