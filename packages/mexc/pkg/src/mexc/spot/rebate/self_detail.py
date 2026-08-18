from mexc.core import Timestamp, timestamp as ts, validator
from typing_extensions import AsyncIterator, TypedDict
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class SelfDetailItem(TypedDict):
  """Rebate record."""
  asset: str
  """Rebate asset."""
  type: str
  """Rebate source type, such as spot or futures."""
  rate: str
  """Rebate rate."""
  amount: str
  """Rebate amount."""
  uid: str
  """Invitee user id."""
  account: str
  """Masked invitee account."""
  tradeTime: Timestamp
  """Trade time in milliseconds."""
  updateTime: Timestamp
  """Record update time in milliseconds."""

class SelfDetailResponse(TypedDict):
  """Paginated rebate response."""
  page: int
  """Current result page."""
  totalRecords: int
  """Total number of matching records."""
  totalPageNum: int
  """Total number of result pages."""
  data: list[SelfDetailItem]
  """Result records for the page."""

Response: type[SelfDetailResponse | ErrorResponse] = SelfDetailResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class SelfDetail(AuthSpotMixin):
  async def self_detail(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    page: int | None = None, recv_window: int | None = None,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> SelfDetailResponse:
    """Returns self-commission rebate records generated from invited friends trading spot or futures.

    Args:
      start_time: Start time in milliseconds.
      end_time: End time in milliseconds.
      page: Result page; defaults to 1.
      recv_window: Optional receive window in milliseconds.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-self-rebate-records-detail)
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
    if recv_window is not None:
      params['recvWindow'] = recv_window
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/rebate/detail/kickback', params=params)
    return self.output(r.text, adapter, validate)

  async def self_detail_paged(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    recv_window: int | None = None, timestamp: Timestamp | None = None,
    max_pages: int | None = None, validate: bool | None = None,
  ) -> AsyncIterator[SelfDetailResponse]:
    """Yield successive pages of `self_detail`.

    Requests `page` from 1 upwards and stops once it has covered the `totalPageNum`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.self_detail(start_time=start_time, end_time=end_time, recv_window=recv_window, timestamp=timestamp, page=page, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('totalPageNum') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or pages >= total:
        break
      page += 1
