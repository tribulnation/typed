"""`GET /api/v1/stopOrders` — Get Stop Order List."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.types import FuturesOrder
from kucoin.core import RpcEndpoint


class FuturesStopOrderPage(TypedDict):
  """One page of untriggered stop orders."""

  currentPage: int
  """Current page number."""
  pageSize: int
  """Results per page, as requested."""
  totalNum: int
  """Total matching stop orders."""
  totalPage: int
  """Total number of pages."""
  items: list[FuturesOrder]
  """Stop orders on this page."""


_Type = FuturesStopOrderPage
adapter = validator[_Type](_Type)  # type: ignore


class GetStopOrderList(RpcEndpoint):
  """`Get Stop Order List` — mixed into `Orders`, the product exposing `futures.orders.get_stop_order_list`."""

  async def get_stop_order_list(
    self,
    *,
    symbol: str | None = None,
    side: Literal['buy', 'sell'] | None = None,
    type: Literal['limit', 'market'] | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    current_page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> FuturesStopOrderPage:
    """List this account's untriggered stop orders. A stop order that has since triggered behaves as a normal order and is found through Get Order List instead.

    Args:
      symbol: Contract symbol to filter by.
      side: Order side to filter by.
      type: Order type to filter by.
      start_at: Start of the time window, Unix milliseconds.
      end_at: End of the time window, Unix milliseconds.
      current_page: Page number.
      page_size: Results per page.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if side is not None:
      params['side'] = side
    if type is not None:
      params['type'] = type
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
      '/api/v1/stopOrders',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def get_stop_order_list_paged(
    self,
    *,
    symbol: str | None = None,
    side: Literal['buy', 'sell'] | None = None,
    type: Literal['limit', 'market'] | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[FuturesStopOrderPage]:
    """Yield successive pages of `get_stop_order_list`.

    Requests `currentPage` from 1 upwards and stops once it has covered the `totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    current_page = 1
    pages = 0
    while True:
      response = await self.get_stop_order_list(
        symbol=symbol,
        side=side,
        type=type,
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
