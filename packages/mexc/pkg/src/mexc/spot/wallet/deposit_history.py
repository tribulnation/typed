from typing_extensions import Literal, NotRequired, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.spot.core import AuthSpotMixin, ErrorResponse

class DepositHistoryItem(TypedDict):
  """Deposit record."""
  amount: str | None
  """Deposit amount."""
  coin: str | None
  """Asset deposited."""
  network: str | None
  """Deposit network."""
  status: int | None
  """Deposit status code."""
  address: str | None
  """Deposit address."""
  addressTag: NotRequired[str | None]
  """Deposit address tag."""
  txId: str | None
  """Blockchain transaction id."""
  insertTime: Timestamp | None
  """Deposit insert time."""
  unlockConfirm: str | None
  """Required confirmations to unlock."""
  confirmTimes: str | None
  """Observed confirmations."""
  memo: str | None
  """Deposit memo."""

Response: type[list[DepositHistoryItem] | ErrorResponse] = list[DepositHistoryItem] | ErrorResponse # type: ignore
adapter = validator(Response)

class DepositHistory(AuthSpotMixin):
  async def deposit_history(
    self, *,
    coin: str | None = None,
    status: Literal['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'] | None = None,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    limit: int | None = None, timestamp: Timestamp | None = None,
    validate: bool | None = None,
  ) -> list[DepositHistoryItem]:
    """Returns deposit records for the signed account, optionally filtered by coin, status, and time window.

    Args:
      coin: Asset filter.
      status: Deposit status filter, as a numeric code: `1` SMALL, `2` TIME_DELAY, `3` LARGE_DELAY, `4` PENDING, `5` SUCCESS, `6` AUDITING, `7` REJECTED, `8` REFUND, `9` PRE_SUCCESS, `10` INVALID, `11` RESTRICTED, `12` COMPLETED.
      start_time: Start time in milliseconds; defaults to seven days ago.
      end_time: End time in milliseconds; defaults to current time.
      limit: Maximum records to return; max 1000.
      timestamp: Signed request timestamp in milliseconds.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/spot_v3_en/#deposit-history-supporting-network)
    """
    if timestamp is None:
      timestamp = ts.parse(ts.now())
    params = {}
    if coin is not None:
      params['coin'] = coin
    if status is not None:
      params['status'] = status
    if start_time is not None:
      params['startTime'] = ts.dump(start_time)
    if end_time is not None:
      params['endTime'] = ts.dump(end_time)
    if limit is not None:
      params['limit'] = limit
    if timestamp is not None:
      params['timestamp'] = ts.dump(timestamp)
    r = await self.signed_request('GET', '/api/v3/capital/deposit/hisrec', params=params)
    return self.output(r.text, adapter, validate)
