"""`GET /api/v1/earn/redeem-preview` — Get Redeem Preview."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class RedeemPreview(TypedDict):
  currency: str
  """Holding currency."""
  redeemAmount: str
  """Amount that would be returned by redeeming."""
  penaltyInterestAmount: str
  """Early-redemption interest penalty that would be forfeited, `"0"` if none applies."""
  redeemPeriod: int
  """Redemption waiting period, in days."""
  deliverTime: int
  """When redeemed funds would be delivered, Unix milliseconds."""
  manualRedeemable: bool
  """Whether this holding can be manually redeemed right now."""
  redeemAll: bool
  """Whether redeeming this holding always redeems it in full (a partial `amount` on `Redeem` would be ignored/rejected)."""


_Type = RedeemPreview
adapter = validator[_Type](_Type)  # type: ignore


class RedeemPreviewEndpoint(RpcEndpoint):
  """`Get Redeem Preview` — mixed into `Earn`, the product exposing `earn.redeem_preview`."""

  async def redeem_preview(
    self,
    *,
    order_id: str,
    from_account_type: Literal['MAIN', 'TRADE'] | None = None,
    validate: bool | None = None,
  ) -> RedeemPreview:
    """Preview what redeeming a specific Earn holding would look like -- amount returned, any early-redemption penalty, and when funds would arrive -- without actually redeeming it. A holding that's already been fully redeemed (or is fully in the process of being redeemed) no longer resolves here.

    Args:
      order_id: Holding id, as returned by `earn.account_holding`'s `orderId`.
      from_account_type: Source account type. Only meaningful for an ETH2 staking holding; irrelevant otherwise.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'orderId': order_id,
    }
    if from_account_type is not None:
      params['fromAccountType'] = from_account_type
    return await self.authed_request(
      'GET',
      '/api/v1/earn/redeem-preview',
      params=params,
      validator=adapter,
      validate=validate,
    )
