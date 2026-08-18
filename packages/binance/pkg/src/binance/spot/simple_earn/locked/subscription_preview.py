from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class LockedSubscriptionPreview(TypedDict):
  """Estimated rewards for a hypothetical locked product subscription."""

  rewardAsset: NotRequired[str]
  """Asset the base rewards would be paid in."""
  totalRewardAmt: NotRequired[str]
  """Total base rewards estimated over the full lock duration, as a decimal string."""
  extraRewardAsset: NotRequired[str]
  """Asset any extra (bonus) reward would be paid in, when applicable."""
  estTotalExtraRewardAmt: NotRequired[str]
  """Estimated total extra (bonus) reward over the full lock duration, as a decimal string."""
  boostRewardAsset: NotRequired[str]
  """Asset any boosted promotional reward would be paid in, when applicable."""
  estDailyRewardAmt: NotRequired[str]
  """Estimated daily base reward, as a decimal string."""
  nextPay: NotRequired[str]
  """Amount of the next reward payment, as a decimal string."""
  nextPayDate: NotRequired[int]
  """Millisecond epoch time of the next reward payment."""
  valueDate: NotRequired[int]
  """Millisecond epoch time the subscription would take effect."""
  rewardsEndDate: NotRequired[int]
  """Millisecond epoch time reward accrual would end."""
  deliverDate: NotRequired[int]
  """Millisecond epoch time principal (and final rewards) would be delivered."""
  nextSubscriptionDate: NotRequired[int]
  """Millisecond epoch time the position would next be eligible to auto-renew into."""


class SubscriptionPreview(RpcEndpoint):
  """Preview the estimated rewards for a hypothetical Simple Earn locked product subscription, without subscribing."""

  async def __call__(
    self,
    *,
    project_id: str,
    amount: str,
    auto_subscribe: bool | None = None,
    validate: bool | None = None,
  ) -> LockedSubscriptionPreview:
    """Preview the estimated rewards for a hypothetical Simple Earn locked product subscription, without subscribing.

    Args:
      project_id: Locked product identifier to preview a subscription for.
      amount: Amount to preview subscribing, as a decimal string.
      auto_subscribe: Whether the previewed position would auto-renew at maturity. Defaults to `true`.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#get-locked-subscription-preview)
    """
    params: dict = {
      'projectId': project_id,
      'amount': amount,
    }
    if auto_subscribe is not None:
      params['autoSubscribe'] = auto_subscribe
    _Response = LockedSubscriptionPreview
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/simple-earn/locked/subscriptionPreview',
      params=params,
      validator=_validator,
      validate=validate,
    )
