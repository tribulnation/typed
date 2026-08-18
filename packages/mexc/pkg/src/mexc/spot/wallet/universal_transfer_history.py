from mexc.core import Timestamp, timestamp as ts, validator
from typing_extensions import TypedDict
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class UniversalTransferRecord(TypedDict):
  """Transfer row."""
  tranId: str | None
  """Transfer id."""
  clientTranId: str | None
  """Client transfer id."""
  asset: str | None
  """Asset."""
  amount: str | None
  """Amount."""
  fromAccountType: str | None
  """Source account type."""
  toAccountType: str | None
  """Destination account type."""
  fromSymbol: str | None
  """Source symbol."""
  toSymbol: str | None
  """Destination symbol."""
  status: str | None
  """Transfer status."""
  timestamp: Timestamp | None
  """Transfer timestamp."""

class UniversalTransferHistoryPage(TypedDict):
  """Universal transfer history page."""
  rows: list[UniversalTransferRecord]
  """Transfer rows."""
  total: int | None
  """Total records."""

Response: type[list[UniversalTransferHistoryPage] | ErrorResponse] = list[UniversalTransferHistoryPage] | ErrorResponse # type: ignore
adapter = validator(Response)

class UniversalTransferHistory(AuthSpotMixin):
  async def universal_transfer_history(
    self, *,
    from_account_type: str, to_account_type: str,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    page: int | None = None, size: int | None = None,
    timestamp: Timestamp | None = None, validate: bool | None = None,
  ) -> list[UniversalTransferHistoryPage]:
    """Returns universal transfer records between account types for the signed account.

    Args:
      from_account_type: Source account type filter.
      to_account_type: Destination account type filter.
      start_time: Start time in milliseconds.
      end_time: End time in milliseconds.
      page: Page number; default 1.
      size: Page size; max 100.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#query-user-universal-transfer-history)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if from_account_type is not None:
      params['fromAccountType'] = from_account_type
    if to_account_type is not None:
      params['toAccountType'] = to_account_type
    if start_time is not None:
      params['startTime'] = ts.dump(start_time)
    if end_time is not None:
      params['endTime'] = ts.dump(end_time)
    if page is not None:
      params['page'] = page
    if size is not None:
      params['size'] = size
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/capital/transfer', params=params)
    return self.output(r.text, adapter, validate)
