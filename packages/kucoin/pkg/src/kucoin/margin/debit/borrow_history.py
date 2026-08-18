"""`GET /api/v3/margin/borrow` — Get Borrow History."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class BorrowHistoryEntry(TypedDict):
  orderNo: str
  """Unique borrow order id."""
  symbol: str
  """Isolated-margin trading pair; the literal `DEFAULT` for a cross-margin borrow, not `null` as the docs describe (confirmed live)."""
  currency: str
  """Borrowed currency."""
  size: str
  """Requested borrow amount."""
  actualSize: str
  """Actual borrowed amount."""
  status: Literal['PENDING', 'SUCCESS', 'FAILED']
  """Borrow order status."""
  createdTime: int
  """Unix milliseconds this borrow was initiated."""


class BorrowHistoryPage(TypedDict):
  """One page of cross/isolated margin borrow orders."""

  timestamp: int
  """Server timestamp, Unix milliseconds."""
  currentPage: int
  """Current page number."""
  pageSize: int
  """Results per page, as requested."""
  totalNum: int
  """Total matching records."""
  totalPage: int
  """Total number of pages."""
  items: list[BorrowHistoryEntry]
  """Borrow orders on this page."""


_Type = BorrowHistoryPage
adapter = validator[_Type](_Type)  # type: ignore


class BorrowHistory(RpcEndpoint):
  """`Get Borrow History` — mixed into `Debit`, the product exposing `margin.debit.borrow_history`."""

  async def borrow_history(
    self,
    *,
    currency: str | None = None,
    is_isolated: bool | None = None,
    symbol: str | None = None,
    order_no: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    current_page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> BorrowHistoryPage:
    """Page through this account's cross- or isolated-margin borrow orders, newest first.

    Args:
      currency: Currency to filter by, e.g. `BTC`, `ETH`, `KCS`. Queries all currencies if omitted.
      is_isolated: Whether to look at isolated-margin (`true`) or cross-margin (`false`) borrows.
      symbol: Trading pair, e.g. `BTC-USDT`. Mandatory for an isolated-margin account.
      order_no: Filter by a specific borrow order id.
      start_time: Start of the time window, Unix milliseconds. Unrestricted; if omitted or below 1680278400000 (2023-04-01T00:00:00Z), that value is used instead.
      end_time: End of the time window, Unix milliseconds.
      current_page: Page number.
      page_size: Results per page.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if currency is not None:
      params['currency'] = currency
    if is_isolated is not None:
      params['isIsolated'] = is_isolated
    if symbol is not None:
      params['symbol'] = symbol
    if order_no is not None:
      params['orderNo'] = order_no
    if start_time is not None:
      params['startTime'] = start_time
    if end_time is not None:
      params['endTime'] = end_time
    if current_page is not None:
      params['currentPage'] = current_page
    if page_size is not None:
      params['pageSize'] = page_size
    return await self.authed_request(
      'GET',
      '/api/v3/margin/borrow',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def borrow_history_paged(
    self,
    *,
    currency: str | None = None,
    is_isolated: bool | None = None,
    symbol: str | None = None,
    order_no: str | None = None,
    start_time: int | None = None,
    end_time: int | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[BorrowHistoryPage]:
    """Yield successive pages of `borrow_history`.

    Requests `currentPage` from 1 upwards and stops once it has covered the `totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    current_page = 1
    pages = 0
    while True:
      response = await self.borrow_history(
        currency=currency,
        is_isolated=is_isolated,
        symbol=symbol,
        order_no=order_no,
        start_time=start_time,
        end_time=end_time,
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
