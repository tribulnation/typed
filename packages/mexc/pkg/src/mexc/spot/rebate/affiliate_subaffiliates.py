from typing_extensions import AsyncIterator, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class AffiliateSubaffiliatesItem(TypedDict):
  """Affiliate record."""
  subaffiliateName: str
  """Sub-affiliate display name."""
  subaffiliateMail: str
  """Masked sub-affiliate email."""
  campaign: str | None
  """Campaign name."""
  inviteCode: str
  """Invite code."""
  activationTime: Timestamp
  """Sub-affiliate activation time."""
  registered: int
  """Registered-user count."""
  deposited: int
  """Deposited-user count."""
  depositAmount: str
  """Deposit amount."""
  commission: str
  """Commission amount."""

class AffiliateSubaffiliatesData(TypedDict):
  """Paginated affiliate data."""
  pageSize: int
  """Number of records requested per page."""
  totalCount: int
  """Total number of matching records."""
  totalPage: int
  """Total number of result pages."""
  currentPage: int
  """Current result page."""
  resultList: list[AffiliateSubaffiliatesItem]
  """Affiliate records for the page."""

class AffiliateSubaffiliatesResponse(TypedDict):
  """Affiliate wrapper response."""
  success: bool
  """Whether the request succeeded."""
  code: int
  """Business response code."""
  message: str | None
  """Business response message."""
  data: AffiliateSubaffiliatesData

Response: type[AffiliateSubaffiliatesResponse | ErrorResponse] = AffiliateSubaffiliatesResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class AffiliateSubaffiliates(AuthSpotMixin):
  async def affiliate_subaffiliates(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    invite_code: str | None = None, page: int | None = None,
    page_size: int | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> AffiliateSubaffiliatesResponse:
    """Affiliate-only endpoint returning sub-affiliate activation, registration, deposit, campaign, and commission data.

    Args:
      start_time: Start time in milliseconds.
      end_time: End time in milliseconds.
      invite_code: Invite code filter.
      page: Result page.
      page_size: Records per page; defaults to 10.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-subaffiliates-data-affiliate-only)
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
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/rebate/affiliate/subaffiliates', params=params)
    return self.output(r.text, adapter, validate)

  async def affiliate_subaffiliates_paged(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    invite_code: str | None = None, page_size: int | None = None,
    timestamp: Timestamp | None = None, max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[AffiliateSubaffiliatesResponse]:
    """Yield successive pages of `affiliate_subaffiliates`.

    Requests `page` from 1 upwards and stops once it has covered the `data.totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.affiliate_subaffiliates(start_time=start_time, end_time=end_time, invite_code=invite_code, page_size=page_size, timestamp=timestamp, page=page, validate=validate)
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
