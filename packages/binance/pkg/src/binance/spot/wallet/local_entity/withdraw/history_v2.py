from typing_extensions import Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class LocalEntityWithdrawalV2(TypedDict):
  """One withdrawal's travel rule detail. Identical shape to v1 (spot.wallet.local_entity.withdraw.history) — the SDK's own response model reuses v1's item model verbatim."""

  id: NotRequired[str]
  """Withdrawal record id."""
  trId: NotRequired[int]
  """Travel rule record id."""
  amount: NotRequired[str]
  """Withdrawal amount."""
  transactionFee: NotRequired[str]
  """Network fee charged for the withdrawal."""
  coin: NotRequired[str]
  """Withdrawal coin."""
  withdrawalStatus: NotRequired[int]
  """Withdrawal status code. Not enumerated on this endpoint's own documentation; see notes. If absent, use trId or txId to retrieve the record instead."""
  travelRuleStatus: NotRequired[Literal[0, 1, 2]]
  """Travel rule status: 0 Completed, 1 Pending, 2 Failed."""
  address: NotRequired[str]
  """Recipient address."""
  txId: NotRequired[str]
  """Transaction hash."""
  applyTime: NotRequired[str]
  """Time the withdrawal was requested."""
  network: NotRequired[str]
  """Withdrawal network. May be absent for older withdrawals."""
  transferType: NotRequired[int]
  """Transfer type code. Not enumerated on this endpoint's own documentation; see notes."""
  withdrawOrderId: NotRequired[str]
  """Caller-supplied withdraw order id, if one was provided at submission time."""
  info: NotRequired[str]
  """Status message."""
  confirmNo: NotRequired[int]
  """On-chain confirmation count."""
  walletType: NotRequired[Literal[0, 1]]
  """Wallet the withdrawal was made from: 0 spot wallet, 1 funding wallet."""
  txKey: NotRequired[str]
  """Transaction key."""
  questionnaire: NotRequired[str]
  """JSON-formatted questionnaire answers submitted with this withdrawal."""
  completeTime: NotRequired[str]
  """Time the withdrawal completed."""


class HistoryV2(RpcEndpoint):
  """Fetch withdraw history for local entities that require travel rule (v2). Same fields as v1, with tighter time-window rules when querying by withdrawOrderId; see notes."""

  async def history_v2(
    self,
    *,
    tr_id: str | None = None,
    tx_id: str | None = None,
    withdraw_order_id: str | None = None,
    network: str | None = None,
    coin: str | None = None,
    travel_rule_status: Literal[0, 1, 2] | None = None,
    offset: int | None = None,
    limit: int | None = None,
    start_time: Timestamp | None = None,
    end_time: Timestamp | None = None,
    validate: bool | None = None,
  ) -> list[LocalEntityWithdrawalV2]:
    """Fetch withdraw history for local entities that require travel rule (v2). Same fields as v1, with tighter time-window rules when querying by withdrawOrderId; see notes.

    Args:
      tr_id: Comma-separated list of travel rule record ids to filter by. Maximum 45 ids.
      tx_id: Comma-separated list of transaction ids to filter by. Maximum 45 ids.
      withdraw_order_id: Client-side id for the withdrawal, if one was provided in spot.wallet.capital.withdraw.apply or spot.wallet.local_entity.withdraw.apply. Only a single id is supported. If sent, startTime/endTime must span under 7 days; if startTime/endTime are also omitted, the last 7 days are returned by default.
      network: Network to filter by.
      coin: Coin to filter by.
      travel_rule_status: Travel rule status to filter by: 0 Completed, 1 Pending, 2 Failed.
      offset: Number of records to skip before the returned page.
      limit: Maximum number of records to return.
      start_time: Start of the query window, as milliseconds since epoch. Defaults to 90 days before the current time (7 days if withdrawOrderId is sent).
      end_time: End of the query window, as milliseconds since epoch. Defaults to the current time.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/core-trading-wallet/api/rest-api/travel-rule#withdraw-history-v2)
    """
    params = {}
    if tr_id is not None:
      params['trId'] = tr_id
    if tx_id is not None:
      params['txId'] = tx_id
    if withdraw_order_id is not None:
      params['withdrawOrderId'] = withdraw_order_id
    if network is not None:
      params['network'] = network
    if coin is not None:
      params['coin'] = coin
    if travel_rule_status is not None:
      params['travelRuleStatus'] = travel_rule_status
    if offset is not None:
      params['offset'] = offset
    if limit is not None:
      params['limit'] = limit
    if start_time is not None:
      params['startTime'] = timestamp.dump(start_time)
    if end_time is not None:
      params['endTime'] = timestamp.dump(end_time)
    _Response = list[LocalEntityWithdrawalV2]
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v2/localentity/withdraw/history',
      params=params,
      validator=_validator,
      validate=validate,
    )
