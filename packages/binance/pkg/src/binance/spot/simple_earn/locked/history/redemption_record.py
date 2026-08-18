from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class LockedRedemptionRecord(TypedDict):
  """One locked product redemption."""

  positionId: NotRequired[int]
  """Identifier of the locked position redeemed."""
  redeemId: NotRequired[int]
  """Identifier of the redemption."""
  time: NotRequired[int]
  """Millisecond epoch time the redemption was recorded."""
  asset: NotRequired[str]
  """Underlying asset redeemed."""
  lockPeriod: NotRequired[str]
  """Lock duration of the redeemed position in days, as a numeric string."""
  amount: NotRequired[str]
  """Redeemed amount, as a decimal string."""
  originalAmount: NotRequired[str]
  """Original principal amount of the position, as a decimal string."""
  type: NotRequired[str]
  """Redemption type (e.g. redemption at maturity vs. an early redemption)."""
  deliverDate: NotRequired[int]
  """Millisecond epoch time the redeemed amount is (or was) delivered."""
  lossAmount: NotRequired[str]
  """Amount forfeited for redeeming early, as a decimal string."""
  isComplete: NotRequired[bool]
  """Whether the redemption has finished settling."""
  rewardAsset: NotRequired[str]
  """Asset the base rewards were paid in."""
  rewardAmt: NotRequired[str]
  """Base rewards paid out with this redemption, as a decimal string."""
  extraRewardAsset: NotRequired[str]
  """Asset any extra (bonus) reward was paid in, when applicable."""
  estExtraRewardAmt: NotRequired[str]
  """Extra (bonus) reward paid out with this redemption, as a decimal string, when applicable."""
  status: NotRequired[str]
  """Redemption status."""


class LockedRedemptionRecordPage(TypedDict):
  """One page of this account's locked product redemption history."""

  rows: NotRequired[list[LockedRedemptionRecord]]
  """Matching records on this page."""
  total: NotRequired[int]
  """Total number of matching records."""


class RedemptionRecord(RpcEndpoint):
  """Get this account's Simple Earn locked product redemption history."""

  async def redemption_record(
    self,
    *,
    position_id: str | None = None,
    redeem_id: str | None = None,
    asset: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> LockedRedemptionRecordPage:
    """Get this account's Simple Earn locked product redemption history.

    Args:
      position_id: Restrict results to this locked position.
      redeem_id: Restrict results to this redemption.
      asset: Restrict results to this underlying asset.
      start_time: Millisecond epoch start of the queried window.
      end_time: Millisecond epoch end of the queried window.
      current: Currently querying page. Starts from 1.
      size: Number of results per page.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/investment-and-services-simple-earn/api/rest-api/flexible-locked#get-locked-redemption-record)
    """
    params = {}
    if position_id is not None:
      params['positionId'] = position_id
    if redeem_id is not None:
      params['redeemId'] = redeem_id
    if asset is not None:
      params['asset'] = asset
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = LockedRedemptionRecordPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/simple-earn/locked/history/redemptionRecord',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def redemption_record_paged(
    self,
    *,
    position_id: str | None = None,
    redeem_id: str | None = None,
    asset: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[LockedRedemptionRecordPage]:
    """Yield successive pages of `redemption_record`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.redemption_record(
        position_id=position_id,
        redeem_id=redeem_id,
        asset=asset,
        start_time=start_time,
        end_time=end_time,
        size=size,
        current=current,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or size is None or pages * size >= total:
        break
      current += 1
