"""`GET /api/v2/affiliate/queryKumining` — Get Kumining."""

from typing_extensions import Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class AffiliateKuminingRecord(TypedDict):
  """One Kumining payout attributed to this affiliate account."""

  uid: str
  """The invitee's UID."""
  payTime: int
  """Unix milliseconds the payout was made."""
  goodsName: str
  """Name of the Kumining product paid out, for example `BTC-10TH`."""
  amount: str
  """Payout amount."""
  currency: str
  """Denomination unit for `amount`. KuCoin does not document a closed set for this field on this endpoint's own page (unlike the sibling Get Invited/Get Commission/Get Trade History/Get Transaction endpoints, which document `USDT`/`USDC` explicitly for their analogous fields), so it's left as a plain string -- see notes."""
  lastId: str
  """This record's cursor id -- pass as the next call's `lastId` to continue paging."""


_Type = list[AffiliateKuminingRecord]
adapter = validator[_Type](_Type)  # type: ignore


class Kumining(RpcEndpoint):
  """`Get Kumining` — mixed into `Affiliate`, the product exposing `affiliate.kumining`."""

  async def kumining(
    self,
    *,
    uid: str | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    last_id: str | None = None,
    direction: Literal['PRE', 'NEXT'] | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> list[AffiliateKuminingRecord]:
    """Walk this affiliate account's Kumining payout records over a time window, cursor-paginated by `lastId`.

    Args:
      uid: Restrict to one invitee's UID.
      start_at: Restrict to payouts at or after this Unix millisecond timestamp.
      end_at: Restrict to payouts at or before this Unix millisecond timestamp.
      last_id: Cursor for the next page: omit for the first page, then pass the `lastId` of the last record from the previous response.
      direction: Which way to page from `lastId`. KuCoin documents no default here, unlike the sibling Get Transaction endpoint's `NEXT`.
      page_size: Results per page.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
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
      '/api/v2/affiliate/queryKumining',
      params=params,
      validator=adapter,
      validate=validate,
    )
