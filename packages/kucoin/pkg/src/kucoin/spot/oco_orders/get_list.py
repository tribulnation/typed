"""`GET /api/v3/oco/orders` — spot.oco_orders.get_list."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp, timestamp


class OcoOrderSummary(TypedDict):
  """Lightweight OCO order summary, with no leg detail."""

  orderId: str
  """OCO order group id."""
  symbol: str
  """Trading pair."""
  clientOid: str
  """Client-provided order id, as supplied at placement."""
  orderTime: Timestamp
  """Time the OCO order was placed."""
  status: Literal['NEW', 'DONE', 'TRIGGERED', 'CANCELLED']
  """OCO order group status."""


class OcoOrderListPage(TypedDict):
  currentPage: int
  """Page number returned."""
  pageSize: int
  """Results per page."""
  totalNum: int
  """Total number of OCO orders matching the filter."""
  totalPage: int
  """Total number of pages."""
  items: list[OcoOrderSummary]
  """OCO order summaries on this page, newest first."""


_Type = OcoOrderListPage
adapter = validator[_Type](_Type)  # type: ignore


class GetList(RpcEndpoint):
  """`spot.oco_orders.get_list` — mixed into `OcoOrders`, the product exposing `spot.oco_orders.get_list`."""

  async def get_list(
    self,
    *,
    symbol: str | None = None,
    start_at: Timestamp | None = None,
    end_at: Timestamp | None = None,
    order_ids: str | None = None,
    page_size: int | None = None,
    current_page: int | None = None,
    validate: bool | None = None,
  ) -> OcoOrderListPage:
    """Get a paginated list of the account's OCO orders, newest first. Rows are the same lightweight shape as Get OCO Order By OrderId, with no leg detail.

    Args:
      symbol: Trading pair to filter by. Omitted returns OCO orders across all symbols.
      start_at: Start time (milliseconds).
      end_at: End time (milliseconds).
      order_ids: Comma-separated order ids to filter by, up to 500.
      page_size: Results per page.
      current_page: Page number to fetch, starting at 1.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if start_at is not None:
      params['startAt'] = timestamp.dump(start_at)
    if end_at is not None:
      params['endAt'] = timestamp.dump(end_at)
    if order_ids is not None:
      params['orderIds'] = order_ids
    if page_size is not None:
      params['pageSize'] = page_size
    if current_page is not None:
      params['currentPage'] = current_page
    return await self.authed_request(
      'GET',
      '/api/v3/oco/orders',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def get_list_paged(
    self,
    *,
    symbol: str | None = None,
    start_at: Timestamp | None = None,
    end_at: Timestamp | None = None,
    order_ids: str | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[OcoOrderListPage]:
    """Yield successive pages of `get_list`.

    Requests `currentPage` from 1 upwards and stops once it has covered the `totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    current_page = 1
    pages = 0
    while True:
      response = await self.get_list(
        symbol=symbol,
        start_at=start_at,
        end_at=end_at,
        order_ids=order_ids,
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
