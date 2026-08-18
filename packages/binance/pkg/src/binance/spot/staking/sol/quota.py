from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class SolStakingQuota(TypedDict):
  """This account's current SOL staking quota and product state."""

  leftStakingPersonalQuota: NotRequired[str]
  """Remaining amount this account may stake, as a decimal string."""
  leftRedemptionPersonalQuota: NotRequired[str]
  """Remaining amount this account may redeem, as a decimal string."""
  minStakeAmount: NotRequired[str]
  """Minimum amount of SOL that can be staked in one call, as a decimal string."""
  minRedeemAmount: NotRequired[str]
  """Minimum amount of BNSOL that can be redeemed in one call, as a decimal string."""
  redeemPeriod: NotRequired[int]
  """Redemption processing period, in days."""
  stakeable: NotRequired[bool]
  """Whether SOL staking is currently open to this account."""
  redeemable: NotRequired[bool]
  """Whether SOL redemption is currently open to this account."""
  soldOut: NotRequired[bool]
  """Whether the SOL staking product's subscription quota is currently exhausted."""
  commissionFee: NotRequired[str]
  """Commission fee rate charged on staking rewards, as a decimal string."""
  nextEpochTime: NotRequired[int]
  """Millisecond epoch time the next Solana staking epoch begins."""
  calculating: NotRequired[bool]
  """Whether the quota figures above are still being recalculated and may not yet be final."""


class Quota(RpcEndpoint):
  """Get this account's current SOL staking subscription and redemption quota."""

  async def __call__(self, *, validate: bool | None = None) -> SolStakingQuota:
    """Get this account's current SOL staking subscription and redemption quota.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/sol-staking#get-sol-staking-quota-details)
    """
    _Response = SolStakingQuota
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/sol-staking/sol/quota', validator=_validator, validate=validate
    )
