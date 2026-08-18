from typing_extensions import AsyncIterator, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class AffiliateReferralItem(TypedDict):
  """Affiliate record."""
  uid: int | str
  """Referral user id."""
  nickName: str | None
  """Referral nickname."""
  email: str
  """Referral email."""
  registerTime: Timestamp
  """Registration time."""
  inviteCode: str
  """Invite code."""
  depositAmount: str
  """Deposit amount in USDT."""
  tradingAmount: str
  """Trading amount in USDT."""
  commission: str
  """Commission amount in USDT."""
  firstDepositTime: Timestamp | None
  """First deposit time."""
  firstTradeTime: Timestamp | None
  """First trade time."""
  lastDepositTime: Timestamp | None
  """Last deposit time."""
  lastTradeTime: Timestamp | None
  """Last trade time."""
  withdrawAmount: str
  """Withdrawal amount in USDT."""
  asset: str
  """Asset balance band."""
  identification: int
  """KYC identification level."""

class AffiliateReferralData(TypedDict):
  """Paginated affiliate data."""
  pageSize: int
  """Number of records requested per page."""
  totalCount: int
  """Total number of matching records."""
  totalPage: int
  """Total number of result pages."""
  currentPage: int
  """Current result page."""
  resultList: list[AffiliateReferralItem]
  """Affiliate records for the page."""

class AffiliateReferralResponse(TypedDict):
  """Affiliate wrapper response."""
  success: bool
  """Whether the request succeeded."""
  code: int
  """Business response code."""
  message: str | None
  """Business response message."""
  data: AffiliateReferralData

Response: type[AffiliateReferralResponse | ErrorResponse] = AffiliateReferralResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class AffiliateReferral(AuthSpotMixin):
  async def affiliate_referral(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    uid: str | None = None, invite_code: str | None = None,
    page: int | None = None, page_size: int | None = None,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> AffiliateReferralResponse:
    """Affiliate-only endpoint returning referred-user deposit, trading, commission, asset-band, and identification data.

    Args:
      start_time: Start time in milliseconds.
      end_time: End time in milliseconds.
      uid: Referral user id filter.
      invite_code: Invite code filter.
      page: Result page.
      page_size: Records per page; defaults to 10.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-affiliate-referral-data-affiliate-only)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if start_time is not None:
      params['startTime'] = ts.dump(start_time)
    if end_time is not None:
      params['endTime'] = ts.dump(end_time)
    if uid is not None:
      params['uid'] = uid
    if invite_code is not None:
      params['inviteCode'] = invite_code
    if page is not None:
      params['page'] = page
    if page_size is not None:
      params['pageSize'] = page_size
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/rebate/affiliate/referral', params=params)
    return self.output(r.text, adapter, validate)

  async def affiliate_referral_paged(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    uid: str | None = None, invite_code: str | None = None,
    page_size: int | None = None, timestamp: Timestamp | None = None,
    max_pages: int | None = None, validate: bool | None = None,
  ) -> AsyncIterator[AffiliateReferralResponse]:
    """Yield successive pages of `affiliate_referral`.

    Requests `page` from 1 upwards and stops once it has covered the `data.totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.affiliate_referral(start_time=start_time, end_time=end_time, uid=uid, invite_code=invite_code, page_size=page_size, timestamp=timestamp, page=page, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total_0 = response.get('data') if response is not None else None
      total = total_0.get('totalPage') if total_0 is not None else None
      total = int(total) if total is not None else None
      if total is None or pages >= total:
        break
      page += 1
