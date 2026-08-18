from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class DepositRecord(TypedDict):
  """One deposit."""

  id: NotRequired[str]
  """Deposit record id."""
  amount: str
  """Deposit amount."""
  coin: str
  """Deposited coin."""
  network: str
  """Network the deposit arrived on."""
  status: Literal[0, 1, 2, 6, 7, 8]
  """Deposit status."""
  address: str
  """Deposit address credited."""
  addressTag: str
  """Memo/tag included with the deposit, for coins/networks that use one."""
  txId: str
  """Transaction hash."""
  insertTime: Timestamp
  """Time the deposit record was created."""
  completeTime: NotRequired[Timestamp]
  """Time the deposit was fully completed and credited."""
  transferType: int
  """Transfer type. Not enumerated on this endpoint's own documentation; see notes."""
  confirmTimes: str
  """On-chain confirmation count, as `<current>/<required>`."""
  unlockConfirm: int
  """Confirmations needed to unlock the credited balance. Corrected from live evidence: the docs-only pass guessed the same `<current>/<required>` string shape as `confirmTimes`, but this account's real response had a bare integer (e.g. `2`)."""
  walletType: NotRequired[int]
  """Wallet the deposit was credited to: `0` for Spot wallet, `1` for Funding wallet."""
  travelRuleStatus: NotRequired[int]
  """Travel rule verification status. Not enumerated in this endpoint's own documentation; see notes."""
  sourceAddress: NotRequired[str]
  """Originating address of the deposit. Present only when `includeSource=true` was requested."""


class History(RpcEndpoint):
  """Fetch deposit history. If both `startTime` and `endTime` are sent, the window between them must be less than 90 days; defaults keep the window within the last 90 days."""

  async def history(
    self,
    *,
    coin: str | None = None,
    status: Literal[0, 1, 2, 6, 7, 8] | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    offset: int | None = None,
    limit: int | None = None,
    tx_id: str | None = None,
    include_source: bool | None = None,
    validate: bool | None = None,
  ) -> list[DepositRecord]:
    """Fetch deposit history. If both `startTime` and `endTime` are sent, the window between them must be less than 90 days; defaults keep the window within the last 90 days.

    Args:
      coin: Coin to filter by. Returns every coin's deposits when omitted.
      status: Deposit status to filter by.
      start_time: Start of the query window, as milliseconds since epoch. Defaults to 90 days before the current time.
      end_time: End of the query window, as milliseconds since epoch. Defaults to the current time.
      offset: Number of records to skip before the returned page.
      limit: Maximum number of records to return.
      tx_id: Transaction hash to filter by.
      include_source: Whether to include the `sourceAddress` field in each returned record.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/capital#deposit-history)
    """
    params = {}
    if coin is not None:
      params['coin'] = coin
    if status is not None:
      params['status'] = status
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    if offset is not None:
      params['offset'] = offset
    if limit is not None:
      params['limit'] = limit
    if tx_id is not None:
      params['txId'] = tx_id
    if include_source is not None:
      params['includeSource'] = include_source
    _Response = list[DepositRecord]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/capital/deposit/hisrec',
      params=params,
      validator=_validator,
      validate=validate,
    )
