"""`GET /api/v1/accounts/ledgers` — Get Account Ledgers - Spot/Margin."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class SpotMarginLedgerEntry(TypedDict):
  id: str
  """Unique ledger entry ID."""
  currency: str
  """Currency."""
  amount: str
  """Total amount involved (fees included)."""
  fee: str
  """Fee charged, if any."""
  balance: str
  """Documented as the resulting account balance, but marked deprecated -- "no actual use of the value"."""
  accountType: Literal['MAIN', 'TRADE', 'MARGIN', 'CONTRACT']
  """Which account type this entry belongs to."""
  bizType: str
  """Business type causing this entry, e.g. exchange, withdrawal, deposit, `KUCOIN_BONUS`, `REFERRAL_BONUS`, `Lendings` (docs give these as examples, not an exhaustive set)."""
  direction: Literal['in', 'out']
  """Fund flow direction."""
  createdAt: int
  """Unix milliseconds this entry occurred."""
  context: str
  """JSON-encoded business context (order ID, transfer ID, etc.), or empty."""


class SpotMarginLedgerPage(TypedDict):
  """One page of Spot/Margin ledger entries."""

  currentPage: int
  """Current page number."""
  pageSize: int
  """Results per page, as requested."""
  totalNum: int
  """Total matching records."""
  totalPage: int
  """Total number of pages."""
  items: list[SpotMarginLedgerEntry]
  """Ledger entries on this page."""


_Type = SpotMarginLedgerPage
adapter = validator[_Type](_Type)  # type: ignore


class Ledgers(RpcEndpoint):
  """`Get Account Ledgers - Spot/Margin` — mixed into `Account`, the product exposing `account.ledgers`."""

  async def ledgers(
    self,
    *,
    currency: str | None = None,
    direction: Literal['in', 'out'] | None = None,
    biz_type: str | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    current_page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> SpotMarginLedgerPage:
    """Page through transaction records across all of the user's Spot/Margin account types, newest first. A time window is required implicitly: if only one of `startAt`/`endAt` is given the other defaults to a point 24h away, and the window between them can never exceed 24h regardless. Up to 1 year of history is retained, capped at 10,000 records per 24h window.

    Args:
      currency: Currency, or up to 10 comma-separated currencies. Queries all currencies if omitted.
      direction: Fund flow direction.
      biz_type: Business type causing the ledger entry, e.g. `DEPOSIT`, `WITHDRAW`, `TRANSFER`, `SUB_TRANSFER`, `TRADE_EXCHANGE`, `MARGIN_EXCHANGE`, `KUCOIN_BONUS`, `BROKER_TRANSFER` (docs list these as examples, not an exhaustive set).
      start_at: Start time, Unix milliseconds.
      end_at: End time, Unix milliseconds.
      current_page: Page number.
      page_size: Results per page.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    if direction is not None:
      params['direction'] = direction
    if biz_type is not None:
      params['bizType'] = biz_type
    if start_at is not None:
      params['startAt'] = start_at
    if end_at is not None:
      params['endAt'] = end_at
    if current_page is not None:
      params['currentPage'] = current_page
    if page_size is not None:
      params['pageSize'] = page_size
    return await self.authed_request(
      'GET',
      '/api/v1/accounts/ledgers',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def ledgers_paged(
    self,
    *,
    currency: str | None = None,
    direction: Literal['in', 'out'] | None = None,
    biz_type: str | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[SpotMarginLedgerPage]:
    """Yield successive pages of `ledgers`.

    Requests `currentPage` from 1 upwards and stops once it has covered the `totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    current_page = 1
    pages = 0
    while True:
      response = await self.ledgers(
        currency=currency,
        direction=direction,
        biz_type=biz_type,
        start_at=start_at,
        end_at=end_at,
        page_size=page_size,
        current_page=current_page,
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
      current_page += 1
