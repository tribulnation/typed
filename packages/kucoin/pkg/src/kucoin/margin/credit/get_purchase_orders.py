"""`GET /api/v3/purchase/orders` — Get Purchase Orders."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class PurchaseOrder(TypedDict):
  currency: str
  """Currency lent."""
  purchaseOrderNo: str
  """Unique purchase order id."""
  purchaseSize: str
  """Total amount lent by this order."""
  matchSize: str
  """Amount of this order matched (actually lent out) so far."""
  interestRate: str
  """Interest rate this order offers."""
  incomeSize: str
  """Interest income earned so far."""
  applyTime: int
  """Unix milliseconds this purchase was submitted."""
  status: Literal['DONE', 'PENDING']
  """Settlement status."""


class PurchaseOrdersPage(TypedDict):
  """One page of margin credit purchase orders."""

  currentPage: int
  """Current page number."""
  pageSize: int
  """Results per page, as applied."""
  totalNum: int
  """Total matching records."""
  totalPage: int
  """Total number of pages."""
  items: list[PurchaseOrder]
  """Purchase orders on this page."""


_Type = PurchaseOrdersPage
adapter = validator[_Type](_Type)  # type: ignore


class GetPurchaseOrders(RpcEndpoint):
  """`Get Purchase Orders` — mixed into `Credit`, the product exposing `margin.credit.get_purchase_orders`."""

  async def get_purchase_orders(
    self,
    *,
    status: Literal['DONE', 'PENDING'],
    currency: str | None = None,
    purchase_order_no: str | None = None,
    current_page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> PurchaseOrdersPage:
    """Page through this account's margin credit purchase (lend) orders, filtered by settlement status.

    Args:
      status: Settlement status to filter by.
      currency: Currency to filter by, e.g. `BTC`, `ETH`, `KCS`. Queries every currency if omitted.
      purchase_order_no: Filter by a specific purchase order id.
      current_page: Page number.
      page_size: Results per page. Documented range 1-50; the SDK's OpenAPI spec claims a default of 50, but a live call omitting this parameter returned `pageSize: 10` -- specced against the observed default.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'status': status,
    }
    if currency is not None:
      params['currency'] = currency
    if purchase_order_no is not None:
      params['purchaseOrderNo'] = purchase_order_no
    if current_page is not None:
      params['currentPage'] = current_page
    if page_size is not None:
      params['pageSize'] = page_size
    return await self.authed_request(
      'GET',
      '/api/v3/purchase/orders',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def get_purchase_orders_paged(
    self,
    *,
    status: Literal['DONE', 'PENDING'],
    currency: str | None = None,
    purchase_order_no: str | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[PurchaseOrdersPage]:
    """Yield successive pages of `get_purchase_orders`.

    Requests `currentPage` from 1 upwards and stops once it has covered the `totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    current_page = 1
    pages = 0
    while True:
      response = await self.get_purchase_orders(
        status=status,
        currency=currency,
        purchase_order_no=purchase_order_no,
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
