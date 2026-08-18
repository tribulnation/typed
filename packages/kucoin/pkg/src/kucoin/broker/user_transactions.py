"""`GET /api/v2/broker/queryDetailByUid` — Get User Transactions."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BrokerUserTransaction(TypedDict):
  """One user's trading summary as of one transaction-detail row."""

  tradeTime: int
  """Trade time, Unix milliseconds."""
  uid: str
  """User UID."""
  nickName: str
  """User nickname, defaults to phone number or email if none set."""
  invitedByMe: bool
  """Whether this user was directly invited by this broker."""
  totalCommission: str
  """Contributed commission."""
  totalVolume: str
  """Trading volume."""
  totalFee: str
  """Trading fee."""
  rcode: str
  """Referral code this user registered with."""
  spotTradingVolumeWithTag: str
  """Tagged spot trading volume."""
  futureTradingVolumeWithTag: str | None
  """Tagged futures trading volume; `null` for a spot-only trade (observed in the docs' own example row)."""
  tradingFeeWithTag: str
  """Tagged trading fee."""
  commissionWithTag: str
  """Commission contributed by tagged trades."""
  spotTradingVolumeWithNoTag: str | None
  """Untagged spot trading volume; `null` when this row's trade was tagged (observed in the docs' own example row)."""
  futureTradingVolumeWithNoTag: str | None
  """Untagged futures trading volume; `null` when this row's trade was tagged or spot-only (observed in the docs' own example row)."""
  tradingFeeWithNoTag: str | None
  """Untagged trading fee; `null` when this row's trade was tagged (observed in the docs' own example row)."""
  commissionWithNoTag: str | None
  """Commission contributed by untagged trades; `null` when this row's trade was tagged (observed in the docs' own example row)."""
  currency: Literal['USDT', 'USDC']
  """Unit for the volume/amount fields."""
  lastId: str
  """This row's own id -- pass as the next request's `lastId` to seek past it."""


_Type = list[BrokerUserTransaction]
adapter = validator[_Type](_Type)  # type: ignore


class UserTransactions(RpcEndpoint):
  """`Get User Transactions` — mixed into `Broker`, the product exposing `broker.user_transactions`."""

  async def user_transactions(
    self,
    *,
    trade_type: Literal['all', 'SPOT', 'FUTURE'] | None = None,
    uid: str | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    last_id: str | None = None,
    direction: Literal['PRE', 'NEXT'] | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> list[BrokerUserTransaction]:
    """Seek through the authenticated API Broker's per-trade transaction detail for its onboarded users, optionally filtered to one user UID and a trade-time range. Cursor-paginated by `lastId`/`direction`, read out of the last row of the previous response -- not `broker.users`'/`broker.commission`'s `page`/`pageSize` walk.

    Args:
      trade_type: Transaction type to restrict the query to.
      uid: Restrict to one user UID.
      start_at: Trade time lower bound, Unix milliseconds.
      end_at: Trade time upper bound, Unix milliseconds.
      last_id: Seek cursor: the `lastId` of the last row of the previous response. Empty on the first request.
      direction: Which way to seek from `lastId`.
      page_size: Page size.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if trade_type is not None:
      params['tradeType'] = trade_type
    if uid is not None:
      params['uid'] = uid
    if start_at is not None:
      params['startAt'] = start_at
    if end_at is not None:
      params['endAt'] = end_at
    if last_id is not None:
      params['lastId'] = last_id
    if direction is not None:
      params['direction'] = direction
    if page_size is not None:
      params['pageSize'] = page_size
    return await self.authed_request(
      'GET',
      '/api/v2/broker/queryDetailByUid',
      params=params,
      validator=adapter,
      validate=validate,
    )
