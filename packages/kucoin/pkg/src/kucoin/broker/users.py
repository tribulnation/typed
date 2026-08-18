"""`GET /api/v2/broker/queryUser` — Get User List."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BrokerUser(TypedDict):
  """One broker-onboarded user's lifetime trading summary. KuCoin's docs collapse this object without per-field descriptions (only a bare `[object {19}]`, undercounting the live example's own 21 keys -- see notes); descriptions below are inferred from the analogous, individually-documented fields on `broker.user_transactions`."""

  uid: str
  """User UID."""
  nickName: str
  """User nickname, defaults to phone number or email if none set."""
  registrationTime: int
  """User registration time, Unix milliseconds."""
  rateUp: bool
  """Whether this user's rate has been upgraded. KuCoin's docs give no further description."""
  totalCommission: str
  """Total commission this user has contributed."""
  totalTradingVolume: str
  """This user's total trading volume."""
  totalFee: str
  """This user's total trading fee."""
  invitedByMe: bool
  """Whether this user was directly invited by this broker."""
  rcode: str | None
  """Referral code this user registered with; `null` when none (observed in the docs' own example row)."""
  tags: str
  """Broker tag this user traded under."""
  spotTradingVolumeWithTag: str
  """Tagged spot trading volume."""
  futureTradingVolumeWithTag: str
  """Tagged futures trading volume."""
  tradingFeeWithTag: str
  """Tagged trading fee."""
  commissionWithTag: str
  """Commission contributed by tagged trades."""
  spotTradingVolumeWithoutTag: str
  """Untagged spot trading volume."""
  futureTradingVolumeWithoutTag: str
  """Untagged futures trading volume."""
  tradingFeeWithoutTag: str
  """Untagged trading fee."""
  commissionWithoutTag: str
  """Commission contributed by untagged trades."""
  currency: str
  """Denomination unit for the volume/amount fields, e.g. `USDT`."""
  futuresTradingVolumeWithTag: str
  """Tagged futures trading volume. Carries the same meaning as `futureTradingVolumeWithTag` (singular) above -- see notes."""
  futuresTradingVolumeWithoutTag: str
  """Untagged futures trading volume. Carries the same meaning as `futureTradingVolumeWithoutTag` (singular) above -- see notes."""


class BrokerUsersResult(TypedDict):
  """One page of a broker's onboarded users."""

  currentPage: int
  """Current page number."""
  pageSize: int
  """Number of items per page."""
  totalNum: int
  """Total number of items."""
  totalPage: int
  """Total number of pages."""
  items: list[BrokerUser]
  """Users on this page."""


_Type = BrokerUsersResult
adapter = validator[_Type](_Type)  # type: ignore


class Users(RpcEndpoint):
  """`Get User List` — mixed into `Broker`, the product exposing `broker.users`."""

  async def users(
    self,
    *,
    trade_type: Literal['all', 'SPOT', 'FUTURE'] | None = None,
    uid: str | None = None,
    rcode: str | None = None,
    tag: str | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> BrokerUsersResult:
    """Page through the authenticated API Broker's onboarded users, with their lifetime trading volume, fee and commission -- broken out by whether the trades carried a broker tag -- optionally filtered by referral code, tag or registration date.

    Args:
      trade_type: Trade type to restrict the query to.
      uid: Restrict to one user UID.
      rcode: Restrict to users who registered through this referral code.
      tag: Restrict to users who traded under this broker tag.
      start_at: Restrict to users who registered at or after this time, Unix milliseconds.
      end_at: Restrict to users who registered at or before this time, Unix milliseconds.
      page: Page number.
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
    if rcode is not None:
      params['rcode'] = rcode
    if tag is not None:
      params['tag'] = tag
    if start_at is not None:
      params['startAt'] = start_at
    if end_at is not None:
      params['endAt'] = end_at
    if page is not None:
      params['page'] = page
    if page_size is not None:
      params['pageSize'] = page_size
    return await self.authed_request(
      'GET',
      '/api/v2/broker/queryUser',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def users_paged(
    self,
    *,
    trade_type: Literal['all', 'SPOT', 'FUTURE'] | None = None,
    uid: str | None = None,
    rcode: str | None = None,
    tag: str | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[BrokerUsersResult]:
    """Yield successive pages of `users`.

    Requests `page` from 1 upwards and stops once it has covered the `totalPage` pages
    the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.users(
        trade_type=trade_type,
        uid=uid,
        rcode=rcode,
        tag=tag,
        start_at=start_at,
        end_at=end_at,
        page_size=page_size,
        page=page,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('totalPage') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or pages >= total:
        break
      page += 1
