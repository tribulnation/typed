from typing_extensions import AsyncIterator, Literal, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class AffiliateCommissionDetailItem(TypedDict):
  """Affiliate record."""
  type: Literal[1, 2, 3]
  """Commission type: 1 spot, 2 futures, 3 ETF."""
  sourceType: int
  """Source type: 1 referral, 2 sub-affiliate."""
  state: int
  """Commission state."""
  date: int
  """Trade date."""
  uid: str
  """User id."""
  rate: float | str
  """Commission rate."""
  symbol: str
  """Trading symbol."""
  takerAmount: str
  """Taker trade amount."""
  makerAmount: str
  """Maker trade amount."""
  amountCurrency: str
  """Trade amount currency."""
  usdtAmount: str
  """USDT trade amount."""
  commission: str
  """Commission amount."""
  currency: str
  """Commission currency."""

class AffiliateCommissionDetailData(TypedDict):
  """Paginated affiliate data."""
  pageSize: int
  """Number of records requested per page."""
  totalCount: int
  """Total number of matching records."""
  totalPage: int
  """Total number of result pages."""
  currentPage: int
  """Current result page."""
  resultList: list[AffiliateCommissionDetailItem]
  """Affiliate records for the page."""
  totalCommissionUsdtAmount: str
  """Total commission in USDT."""
  totalTradeUsdtAmount: str
  """Total trade volume in USDT."""

class AffiliateCommissionDetailResponse(TypedDict):
  """Affiliate wrapper response."""
  success: bool
  """Whether the request succeeded."""
  code: int
  """Business response code."""
  message: str | None
  """Business response message."""
  data: AffiliateCommissionDetailData

Response: type[AffiliateCommissionDetailResponse | ErrorResponse] = AffiliateCommissionDetailResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class AffiliateCommissionDetail(AuthSpotMixin):
  async def affiliate_commission_detail(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    invite_code: str | None = None, page: int | None = None,
    page_size: int | None = None, type_: Literal[1, 2, 3] | None = None,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> AffiliateCommissionDetailResponse:
    """Affiliate-only endpoint returning detailed commission records by type, source, date, user, and asset.

    Args:
      start_time: Start time in milliseconds.
      end_time: End time in milliseconds.
      invite_code: Invite code filter.
      page: Result page.
      page_size: Records per page; defaults to 10.
      type_: Commission type: 1 spot, 2 futures, 3 ETF.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-affiliate-commission-detail-record-affiliate-only)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if start_time is not None:
      params['startTime'] = ts.dump(start_time)
    if end_time is not None:
      params['endTime'] = ts.dump(end_time)
    if invite_code is not None:
      params['inviteCode'] = invite_code
    if page is not None:
      params['page'] = page
    if page_size is not None:
      params['pageSize'] = page_size
    if type_ is not None:
      params['type'] = type_
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/rebate/affiliate/commission/detail', params=params)
    return self.output(r.text, adapter, validate)

  async def affiliate_commission_detail_paged(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    invite_code: str | None = None, page_size: int | None = None,
    type_: Literal[1, 2, 3] | None = None, timestamp: Timestamp | None = None,
    max_pages: int | None = None, validate: bool | None = None,
  ) -> AsyncIterator[AffiliateCommissionDetailResponse]:
    """Yield successive pages of `affiliate_commission_detail`.

    Requests `page` from 1 upwards and stops once it has covered the `data.totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.affiliate_commission_detail(start_time=start_time, end_time=end_time, invite_code=invite_code, page_size=page_size, type_=type_, timestamp=timestamp, page=page, validate=validate)
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
