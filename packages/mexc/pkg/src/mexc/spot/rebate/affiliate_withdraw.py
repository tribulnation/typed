from typing_extensions import AsyncIterator, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class AffiliateWithdrawItem(TypedDict):
  """Affiliate record."""
  withdrawTime: Timestamp
  """Affiliate withdrawal time."""
  asset: str
  """Withdrawn asset."""
  amount: str
  """Withdraw amount."""

class AffiliateWithdrawData(TypedDict):
  """Paginated affiliate data."""
  pageSize: int
  """Number of records requested per page."""
  totalCount: int
  """Total number of matching records."""
  totalPage: int
  """Total number of result pages."""
  currentPage: int
  """Current result page."""
  resultList: list[AffiliateWithdrawItem]
  """Affiliate records for the page."""

class AffiliateWithdrawResponse(TypedDict):
  """Affiliate wrapper response."""
  success: bool
  """Whether the request succeeded."""
  code: int
  """Business response code."""
  message: str | None
  """Business response message."""
  data: AffiliateWithdrawData

Response: type[AffiliateWithdrawResponse | ErrorResponse] = AffiliateWithdrawResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class AffiliateWithdraw(AuthSpotMixin):
  async def affiliate_withdraw(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    page: int | None = None, page_size: int | None = None,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> AffiliateWithdrawResponse:
    """Affiliate-only endpoint returning affiliate commission withdrawal records.

    Args:
      start_time: Start time in milliseconds.
      end_time: End time in milliseconds.
      page: Result page.
      page_size: Records per page; defaults to 10.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-affiliate-withdraw-record-affiliate-only)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if start_time is not None:
      params['startTime'] = ts.dump(start_time)
    if end_time is not None:
      params['endTime'] = ts.dump(end_time)
    if page is not None:
      params['page'] = page
    if page_size is not None:
      params['pageSize'] = page_size
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/rebate/affiliate/withdraw', params=params)
    return self.output(r.text, adapter, validate)

  async def affiliate_withdraw_paged(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    page_size: int | None = None, timestamp: Timestamp | None = None,
    max_pages: int | None = None, validate: bool | None = None,
  ) -> AsyncIterator[AffiliateWithdrawResponse]:
    """Yield successive pages of `affiliate_withdraw`.

    Requests `page` from 1 upwards and stops once it has covered the `data.totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.affiliate_withdraw(start_time=start_time, end_time=end_time, page_size=page_size, timestamp=timestamp, page=page, validate=validate)
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
