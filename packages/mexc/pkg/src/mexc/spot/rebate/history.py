from mexc.core import Timestamp, timestamp as ts, validator
from typing_extensions import AsyncIterator, TypedDict
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class HistoryItem(TypedDict):
  """Rebate record."""
  spot: str
  """Spot rebate amount in USDT."""
  futures: str
  """Futures rebate amount in USDT."""
  total: str
  """Total rebate amount in USDT."""
  uid: str
  """Invitee user id."""
  account: str
  """Masked invitee account."""
  inviteTime: Timestamp
  """Invite time in milliseconds."""

class HistoryResponse(TypedDict):
  """Paginated rebate response."""
  page: int
  """Current result page."""
  totalRecords: int
  """Total number of matching records."""
  totalPageNum: int
  """Total number of result pages."""
  data: list[HistoryItem]
  """Result records for the page."""

Response: type[HistoryResponse | ErrorResponse] = HistoryResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class History(AuthSpotMixin):
  async def history(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    page: int | None = None, recv_window: int | None = None,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> HistoryResponse:
    """Returns aggregated rebate history for users invited by the signed account.

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
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#get-rebate-history-records)
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
    r = await self.signed_request('GET', '/api/v3/rebate/taxQuery', params=params)
    return self.output(r.text, adapter, validate)

  async def history_paged(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    recv_window: int | None = None, timestamp: Timestamp | None = None,
    max_pages: int | None = None, validate: bool | None = None,
  ) -> AsyncIterator[HistoryResponse]:
    """Yield successive pages of `history`.

    Requests `page` from 1 upwards and stops once it has covered the `totalPageNum`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.history(start_time=start_time, end_time=end_time, recv_window=recv_window, timestamp=timestamp, page=page, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('totalPageNum') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or pages >= total:
        break
      page += 1
