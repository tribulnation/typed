from typing_extensions import NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class BfusdFastRedemptionQuota(TypedDict):
  """Remaining fast-redemption quota."""

  leftQuota: NotRequired[str]
  """Remaining fast-redeemable amount, as a decimal string."""
  minimum: NotRequired[str]
  """Minimum fast redemption amount, as a decimal string."""
  fee: NotRequired[str]
  """Fast redemption fee rate, as a decimal string."""
  freeQuota: NotRequired[str]
  """Amount that can be fast-redeemed with no fee, as a decimal string."""


class BfusdStandardRedemptionQuota(TypedDict):
  """Remaining standard-redemption quota."""

  leftQuota: NotRequired[str]
  """Remaining standard-redeemable amount, as a decimal string."""
  minimum: NotRequired[str]
  """Minimum standard redemption amount, as a decimal string."""
  fee: NotRequired[str]
  """Standard redemption fee rate, as a decimal string."""
  redeemPeriod: NotRequired[int]
  """Standard redemption settlement period, in days."""


class BfusdSubscriptionQuota(TypedDict):
  """Remaining subscription quota."""

  leftQuota: NotRequired[str]
  """Remaining subscribable amount, as a decimal string."""


class BfusdQuota(TypedDict):
  """Subscription and redemption quota for BFUSD."""

  subscriptionQuota: NotRequired[BfusdSubscriptionQuota]
  fastRedemptionQuota: NotRequired[BfusdFastRedemptionQuota]
  standardRedemptionQuota: NotRequired[BfusdStandardRedemptionQuota]


class Quota(RpcEndpoint):
  """Get BFUSD quota details: subscription quota, fast redemption quota, and standard redemption quota."""

  async def __call__(self, *, validate: bool | None = None) -> BfusdQuota:
    """Get BFUSD quota details: subscription quota, fast redemption quota, and standard redemption quota.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/bfusd#get-bfusd-quota-details)
    """
    _Response = BfusdQuota
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET', '/sapi/v1/bfusd/quota', validator=_validator, validate=validate
    )
