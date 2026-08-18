from mexc.core import Timestamp, timestamp as ts, validator
from typing_extensions import Literal, TypedDict
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class WithdrawHistoryItem(TypedDict):
  """Withdrawal record."""
  id: str | None
  """Withdrawal id."""
  txId: str | None
  """Blockchain transaction id."""
  coin: str | None
  """Asset withdrawn."""
  network: str | None
  """Withdrawal network."""
  address: str | None
  """Withdrawal address."""
  amount: str | None
  """Withdrawal amount."""
  transferType: int | None
  """Transfer type; outside or inside transfer."""
  status: int | None
  """Withdrawal status code."""
  transactionFee: str | None
  """Withdrawal fee."""
  applyTime: Timestamp | None
  """Apply time."""
  remark: str | None
  """Remark."""
  memo: str | None
  """Memo."""
  transHash: str | None
  """Transaction hash."""
  updateTime: Timestamp | None
  """Update time."""
  coinId: str | None
  """Asset id."""
  vcoinId: str | None
  """Currency id."""
  confirmNo: None
  """Returned confirmNo field."""

Response: type[list[WithdrawHistoryItem] | ErrorResponse] = list[WithdrawHistoryItem] | ErrorResponse # type: ignore
adapter = validator(Response)

class WithdrawHistory(AuthSpotMixin):
  async def withdraw_history(
    self, *,
    coin: str | None = None,
    status: Literal['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'] | None = None,
    limit: int | None = None, start_time: Timestamp | None = None,
    end_time: Timestamp | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> list[WithdrawHistoryItem]:
    """Returns withdrawal records for the signed account, optionally filtered by coin, status, and time window.

    Args:
      coin: Asset filter.
      status: Withdrawal status filter, as a numeric code: `1` APPLY, `2` AUDITING, `3` WAIT, `4` PROCESSING, `5` WAIT_PACKAGING, `6` WAIT_CONFIRM, `7` SUCCESS, `8` FAILED, `9` CANCEL, `10` MANUAL.
      limit: Maximum records to return; max 1000.
      start_time: Start time in milliseconds; defaults to seven days ago.
      end_time: End time in milliseconds; defaults to current time.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#withdraw-history-supporting-network)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if coin is not None:
      params['coin'] = coin
    if status is not None:
      params['status'] = status
    if limit is not None:
      params['limit'] = limit
    if start_time is not None:
      params['startTime'] = ts.dump(start_time)
    if end_time is not None:
      params['endTime'] = ts.dump(end_time)
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/capital/withdraw/history', params=params)
    return self.output(r.text, adapter, validate)
