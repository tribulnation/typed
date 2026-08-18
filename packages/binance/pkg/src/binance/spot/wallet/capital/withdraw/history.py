from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class WithdrawRecord(TypedDict):
  """One withdrawal."""

  id: str
  """Withdrawal id."""
  amount: str
  """Withdrawal amount."""
  transactionFee: str
  """Network fee charged for this withdrawal."""
  coin: str
  """Withdrawn coin."""
  status: Literal[0, 2, 3, 4, 6]
  """Withdrawal status."""
  address: str
  """Destination withdrawal address."""
  txId: str
  """Transaction hash."""
  applyTime: str
  """Time the withdrawal was submitted, as `YYYY-MM-DD HH:MM:SS`."""
  network: str
  """Network the withdrawal was sent over. May be absent for old withdrawals predating network support."""
  transferType: Literal[0, 1]
  """Transfer type: `1` for internal transfer, `0` for external transfer."""
  withdrawOrderId: NotRequired[str]
  """Caller-supplied idempotency id for this withdrawal, as sent to `capital.withdraw.apply`. Absent when none was supplied."""
  info: NotRequired[str]
  """Reason for withdrawal failure. Present only on a failed withdrawal."""
  confirmNo: NotRequired[int]
  """On-chain confirmation count."""
  walletType: NotRequired[int]
  """Wallet the withdrawal was sent from: `0` for Spot wallet, `1` for Funding wallet."""
  txKey: NotRequired[str]
  """Additional transaction identifier."""
  completeTime: NotRequired[str]
  """Time the withdrawal completed, as `YYYY-MM-DD HH:MM:SS`. Absent while still pending."""


class History(RpcEndpoint):
  """Fetch withdraw history. If both `startTime` and `endTime` are sent, the window between them must be less than 90 days; if `withdrawOrderId` is sent, the window must be less than 7 days, and defaults to the last 7 days when `startTime`/`endTime` are also omitted. Otherwise defaults to the last 90 days."""

  async def history(
    self,
    *,
    coin: str | None = None,
    withdraw_order_id: str | None = None,
    status: Literal[0, 2, 3, 4, 6] | None = None,
    offset: int | None = None,
    limit: int | None = None,
    id_list: str | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    validate: bool | None = None,
  ) -> list[WithdrawRecord]:
    """Fetch withdraw history. If both `startTime` and `endTime` are sent, the window between them must be less than 90 days; if `withdrawOrderId` is sent, the window must be less than 7 days, and defaults to the last 7 days when `startTime`/`endTime` are also omitted. Otherwise defaults to the last 90 days.

    Args:
      coin: Coin to filter by. Returns every coin's withdrawals when omitted.
      withdraw_order_id: Caller-supplied withdrawal id to filter by, as previously sent to `capital.withdraw.apply`.
      status: Withdrawal status to filter by.
      offset: Number of records to skip before the returned page. Default 0.
      limit: Maximum number of records to return.
      id_list: Comma-separated withdrawal ids to filter by, as previously returned by `capital.withdraw.apply`. Supports up to 45 ids.
      start_time: Start of the query window, as milliseconds since epoch. Defaults to 90 days before the current time.
      end_time: End of the query window, as milliseconds since epoch. Defaults to the current time.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#withdraw-history)
    """
    params = {}
    if coin is not None:
      params['coin'] = coin
    if withdraw_order_id is not None:
      params['withdrawOrderId'] = withdraw_order_id
    if status is not None:
      params['status'] = status
    if offset is not None:
      params['offset'] = offset
    if limit is not None:
      params['limit'] = limit
    if id_list is not None:
      params['idList'] = id_list
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    _Response = list[WithdrawRecord]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/capital/withdraw/history',
      params=params,
      validator=_validator,
      validate=validate,
    )
