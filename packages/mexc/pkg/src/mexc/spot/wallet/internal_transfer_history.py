from mexc.core import Timestamp, timestamp as ts, validator
from typing_extensions import AsyncIterator, TypedDict
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class InternalTransferHistoryItem(TypedDict):
  """Internal transfer row."""
  tranId: str | None
  """Transfer id."""
  asset: str | None
  """Asset."""
  amount: str | None
  """Amount."""
  toAccountType: str | None
  """Recipient account type."""
  toAccount: str | None
  """Recipient account."""
  fromAccount: str | None
  """Source account."""
  status: str | None
  """Transfer status."""
  timestamp: Timestamp | None
  """Transfer timestamp."""

class InternalTransferHistoryResponse(TypedDict):
  """Internal transfer history response."""
  page: int | None
  """Current page."""
  totalRecords: int | None
  """Total records."""
  totalPageNum: int | None
  """Total pages."""
  data: list[InternalTransferHistoryItem]
  """Internal transfer rows."""

Response: type[InternalTransferHistoryResponse | ErrorResponse] = InternalTransferHistoryResponse | ErrorResponse # type: ignore
adapter = validator(Response)

class InternalTransferHistory(AuthSpotMixin):
  async def internal_transfer_history(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    page: int | None = None, limit: int | None = None, tran_id: str | None = None,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> InternalTransferHistoryResponse:
    """Returns internal transfer records for the signed account.

    Args:
      start_time: Start time in milliseconds; defaults to seven days ago.
      end_time: End time in milliseconds.
      page: Page number; default 1.
      limit: Page size; default 10.
      tran_id: Transfer id filter.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-internal-transfer-history)
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
    if limit is not None:
      params['limit'] = limit
    if tran_id is not None:
      params['tranId'] = tran_id
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/capital/transfer/internal', params=params)
    return self.output(r.text, adapter, validate)

  async def internal_transfer_history_paged(
    self, *,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    limit: int | None = None, tran_id: str | None = None,
    timestamp: Timestamp | None = None, max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[InternalTransferHistoryResponse]:
    """Yield successive pages of `internal_transfer_history`.

    Requests `page` from 1 upwards and stops on the first page shorter than `limit`, or
    after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.internal_transfer_history(start_time=start_time, end_time=end_time, limit=limit, tran_id=tran_id, timestamp=timestamp, page=page, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('data') if response is not None else None
      if not rows or (limit is not None and len(rows) < limit):
        break
      page += 1
