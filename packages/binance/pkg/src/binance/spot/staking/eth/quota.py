from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class EthStakingQuota(TypedDict):
  """This account's current ETH staking quota and product state."""

  leftStakingPersonalQuota: NotRequired[str]
  """Remaining amount this account may stake, as a decimal string (the lesser of the daily available limit and this account's total personal staking quota)."""
  leftRedemptionPersonalQuota: NotRequired[str]
  """Remaining amount this account may redeem, as a decimal string (the lesser of the daily personal redeem quota and the total redemption limit)."""
  minStakeAmount: NotRequired[str]
  """Minimum amount of ETH that can be staked in one call, as a decimal string."""
  minRedeemAmount: NotRequired[str]
  """Minimum amount of WBETH/BETH that can be redeemed in one call, as a decimal string."""
  redeemPeriod: NotRequired[int]
  """Redemption processing period, in days."""
  stakeable: NotRequired[bool]
  """Whether ETH staking is currently open to this account."""
  redeemable: NotRequired[bool]
  """Whether ETH redemption is currently open to this account."""
  commissionFee: NotRequired[str]
  """Commission fee rate charged on staking rewards, as a decimal string."""
  calculating: NotRequired[bool]
  """Whether the quota figures above are still being recalculated and may not yet be final."""


class Quota(RpcEndpoint):
  """Get this account's current ETH staking subscription and redemption quota."""

  async def __call__(self, *, validate: bool | None = None) -> EthStakingQuota:
    """Get this account's current ETH staking subscription and redemption quota.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/eth-staking#get-current-eth-staking-quota)
    """
    _Response = EthStakingQuota
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/eth-staking/eth/quota', validator=_validator, validate=validate
    )
