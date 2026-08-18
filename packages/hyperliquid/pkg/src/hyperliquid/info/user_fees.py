from typing_extensions import Any, Literal
from typed_core.validation import TypedDict
import pydantic

from hyperliquid.info.core import InfoMixin


class ActiveStakingDiscount(TypedDict):
  """A user's currently active staking-based fee discount."""

  bpsOfMaxSupply: str
  """This user's staked HYPE, in basis points of max token supply, as a decimal string."""
  discount: str
  """This user's currently active staking fee discount, as a decimal string fraction."""


class DailyVolumeEntry(TypedDict):
  """One day of a user's trading volume, alongside exchange-wide volume for that day."""

  date: str
  """Date this volume was recorded for, as an ISO-8601 date (`YYYY-MM-DD`)."""
  userCross: str
  """This user's cross-margin (taker) trading volume on this date, as a decimal string."""
  userAdd: str
  """This user's add-liquidity (maker) trading volume on this date, as a decimal string."""
  exchange: str
  """Exchange-wide trading volume on this date, as a decimal string."""


class MakerFeeTier(TypedDict):
  """One market-maker volume-based fee tier."""

  makerFractionCutoff: str
  """Minimum maker-volume fraction to qualify for this market-maker tier, as a decimal string fraction."""
  add: str
  """Add-liquidity (maker) fee rate at this tier, as a decimal string fraction. Negative values are rebates."""


class StakingDiscountTier(TypedDict):
  """One staking-based fee-discount tier."""

  bpsOfMaxSupply: str
  """Minimum HYPE staked, in basis points of max token supply, to qualify for this tier, as a decimal string."""
  discount: str
  """Fee discount at this tier, as a decimal string fraction."""


class StakingLink(TypedDict):
  """Link between this trading account and a staking account."""

  type: str
  """Kind of staking link. Only `tradingUser` has been observed; Hyperliquid does not document the full set of values."""
  stakingUser: str
  """Address of the staking account linked to this user for fee-discount purposes."""


class UserFeesAction(TypedDict):
  type: Literal['userFees']
  user: str


class VipFeeTier(TypedDict):
  """One VIP volume-based fee tier."""

  ntlCutoff: str
  """Minimum trailing 14-day notional trading volume (USDC) to qualify for this tier, as a decimal string."""
  cross: str
  """Perp cross-margin (taker) fee rate at this tier, as a decimal string fraction."""
  add: str
  """Perp add-liquidity (maker) fee rate at this tier, as a decimal string fraction."""
  spotCross: str
  """Spot cross-margin (taker) fee rate at this tier, as a decimal string fraction."""
  spotAdd: str
  """Spot add-liquidity (maker) fee rate at this tier, as a decimal string fraction."""


class FeeTiers(TypedDict):
  """Volume-based fee tier schedules."""

  vip: list[VipFeeTier]
  """VIP volume-based fee tiers, in ascending order of `ntlCutoff`."""
  mm: list[MakerFeeTier]
  """Market-maker volume-based fee tiers, in ascending order of `makerFractionCutoff`."""


class FeeSchedule(TypedDict):
  """Hyperliquid's base fee rates and volume/staking-based discount schedules."""

  cross: str
  """Base perp cross-margin (taker) fee rate, as a decimal string fraction."""
  add: str
  """Base perp add-liquidity (maker) fee rate, as a decimal string fraction."""
  spotCross: str
  """Base spot cross-margin (taker) fee rate, as a decimal string fraction."""
  spotAdd: str
  """Base spot add-liquidity (maker) fee rate, as a decimal string fraction."""
  tiers: FeeTiers
  referralDiscount: str
  """Fee discount applied to a referred user, as a decimal string fraction."""
  stakingDiscountTiers: list[StakingDiscountTier]
  """Staking-based fee-discount tiers, in ascending order of `bpsOfMaxSupply`."""


class UserFeesResponse(TypedDict):
  """A user's fee schedule and current effective rates."""

  dailyUserVlm: list[DailyVolumeEntry]
  """This user's trading volume for each of the trailing days, alongside exchange-wide volume for the same days."""
  feeSchedule: FeeSchedule
  userCrossRate: str
  """This user's current effective perp cross-margin (taker) fee rate, as a decimal string fraction."""
  userAddRate: str
  """This user's current effective perp add-liquidity (maker) fee rate, as a decimal string fraction."""
  userSpotCrossRate: str
  """This user's current effective spot cross-margin (taker) fee rate, as a decimal string fraction."""
  userSpotAddRate: str
  """This user's current effective spot add-liquidity (maker) fee rate, as a decimal string fraction."""
  activeReferralDiscount: str
  """This user's currently active referral fee discount, as a decimal string fraction."""
  trial: dict[str, Any] | None
  """A fee trial applied to this user, or `null` when none is active."""
  feeTrialEscrow: str
  """Amount held in escrow for an active fee trial (USDC), as a decimal string. Hyperliquid's docs name this field `feeTrialReward`; captured live responses return it as `feeTrialEscrow`."""
  nextTrialAvailableTimestamp: int | None
  """Time the next fee trial becomes available, in milliseconds since epoch, or `null` when none is scheduled."""
  stakingLink: StakingLink | None
  """Staking account linked to this user for fee-discount purposes, or `null` when none is linked."""
  activeStakingDiscount: ActiveStakingDiscount


adapter = pydantic.TypeAdapter(UserFeesResponse)


class UserFees(InfoMixin):
  async def user_fees(self, *, user: str) -> UserFeesResponse:
    """Retrieve a user's fee schedule and current effective rates: base and tiered fee rates, this user's trailing daily volume, their active referral and staking discounts, and any active fee trial.

    Args:
      user: Address to look up, as a 42-character hexadecimal string.

    References:
      - [Official docs](https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint)
    """
    params: UserFeesAction = {
      'type': 'userFees',
      'user': user,
    }
    r = await self.request(params)
    return adapter.validate_python(r) if self.validate else r
