from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class OnChainYieldsLockedSubscriptionPreview(TypedDict):
  """Estimated rewards for a hypothetical On-chain Yields locked product subscription."""

  rewardAsset: NotRequired[str]
  """Asset the base rewards would be paid in."""
  totalRewardAmt: NotRequired[str]
  """Total base rewards estimated over the full lock duration, as a decimal string."""
  nextPay: NotRequired[str]
  """Amount of the next reward payment, as a decimal string."""
  nextPayDate: NotRequired[str]
  """Millisecond epoch time of the next reward payment, as a numeric string."""
  rewardsPayDate: NotRequired[str]
  """Millisecond epoch time of the next scheduled rewards payment, as a numeric string."""
  valueDate: NotRequired[str]
  """Millisecond epoch time the subscription would take effect, as a numeric string."""
  rewardsEndDate: NotRequired[str]
  """Millisecond epoch time reward accrual would end, as a numeric string."""
  deliverDate: NotRequired[str]
  """Millisecond epoch time principal (and final rewards) would be delivered, as a numeric string."""
  nextSubscriptionDate: NotRequired[str]
  """Millisecond epoch time the position would next be eligible to auto-renew into, as a numeric string."""


class SubscriptionPreview(RpcEndpoint):
  """Preview the estimated rewards for a hypothetical On-chain Yields locked product subscription, without subscribing."""

  async def __call__(
    self,
    *,
    project_id: str,
    amount: str,
    auto_subscribe: bool | None = None,
    validate: bool | None = None,
  ) -> OnChainYieldsLockedSubscriptionPreview:
    """Preview the estimated rewards for a hypothetical On-chain Yields locked product subscription, without subscribing.

    Args:
      project_id: Locked product identifier to preview a subscription for.
      amount: Amount to preview subscribing, as a decimal string.
      auto_subscribe: Whether the previewed position would auto-renew at maturity.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-staking/api/rest-api/on-chain-yields#get-on-chain-yields-locked-subscription-preview)
    """
    params: dict = {
      'projectId': project_id,
      'amount': amount,
    }
    if auto_subscribe is not None:
      params['autoSubscribe'] = auto_subscribe
    _Response = OnChainYieldsLockedSubscriptionPreview
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/onchain-yields/locked/subscriptionPreview',
      params=params,
      validator=_validator,
      validate=validate,
    )
