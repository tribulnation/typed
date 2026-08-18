"""`GET /api/v2/affiliate/queryTransactionByUid` — Get Trade History."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class AffiliateTradeHistoryRecord(TypedDict):
  """One trade the invitee made and the commission it generated."""

  tradeTime: int
  """Unix milliseconds the trade executed."""
  tradeType: Literal['SPOT', 'FEATURE']
  """Trading type. `FEATURE` is KuCoin's own documented value here (not `FUTURES`)."""
  tradeCurrency: str
  """Trading pair symbol."""
  tradeAmount: str
  """Trade amount, denominated in the trading pair's own currency."""
  tradeAmountU: str
  """Trade amount converted to `currency`."""
  feeU: str
  """Trading fee converted to `currency`."""
  commission: str
  """Commission this trade generated for the affiliate."""
  currency: Literal['USDT', 'USDC']
  """Denomination unit `tradeAmountU`/`feeU` are converted to."""


class AffiliateTradeHistoryPage(TypedDict):
  """One page of an invitee's trade history."""

  currentPage: int
  """Current page number."""
  pageSize: int
  """Results per page, as applied."""
  totalNum: int
  """Total matching trades."""
  totalPage: int
  """Total number of pages."""
  items: list[AffiliateTradeHistoryRecord]
  """Trades on this page."""


_Type = AffiliateTradeHistoryPage | None
adapter = validator[_Type](_Type)  # type: ignore


class TradeHistory(RpcEndpoint):
  """`Get Trade History` — mixed into `Affiliate`, the product exposing `affiliate.trade_history`."""

  async def trade_history(
    self,
    *,
    uid: str,
    trade_type: Literal['SPOT', 'FEATURE'] | None = None,
    trade_start_at: int | None = None,
    trade_end_at: int | None = None,
    page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> AffiliateTradeHistoryPage | None:
    """Page through one invitee's trade history and the commission each trade generated for this affiliate account.

    Args:
      uid: The invitee's UID to fetch trade history for.
      trade_type: Restrict to one trading type. `FEATURE` is KuCoin's own documented value here (not `FUTURES`).
      trade_start_at: Restrict to trades at or after this Unix millisecond timestamp. If `tradeEndAt` is also given, must be earlier than it.
      trade_end_at: Restrict to trades at or before this Unix millisecond timestamp. If `tradeStartAt` is also given, must be later than it.
      page: Page number.
      page_size: Results per page.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'uid': uid,
    }
    if trade_type is not None:
      params['tradeType'] = trade_type
    if trade_start_at is not None:
      params['tradeStartAt'] = trade_start_at
    if trade_end_at is not None:
      params['tradeEndAt'] = trade_end_at
    if page is not None:
      params['page'] = page
    if page_size is not None:
      params['pageSize'] = page_size
    return await self.authed_request(
      'GET',
      '/api/v2/affiliate/queryTransactionByUid',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def trade_history_paged(
    self,
    *,
    uid: str,
    trade_type: Literal['SPOT', 'FEATURE'] | None = None,
    trade_start_at: int | None = None,
    trade_end_at: int | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[AffiliateTradeHistoryPage | None]:
    """Yield successive pages of `trade_history`.

    Requests `page` from 1 upwards and stops once it has covered the `totalPage` pages
    the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.trade_history(
        uid=uid,
        trade_type=trade_type,
        trade_start_at=trade_start_at,
        trade_end_at=trade_end_at,
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
