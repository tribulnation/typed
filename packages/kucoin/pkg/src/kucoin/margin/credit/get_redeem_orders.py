"""`GET /api/v3/redeem/orders` — Get Redeem Orders."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint


class RedeemOrder(TypedDict):
  currency: str
  """Currency redeemed."""
  purchaseOrderNo: str
  """Id of the purchase order this redeem draws down."""
  redeemOrderNo: str
  """Unique redeem order id."""
  redeemSize: str
  """Amount requested to redeem."""
  receiptSize: str
  """Amount actually received."""
  applyTime: int | None
  """Unix milliseconds this redeem was submitted, or `null` -- KuCoin's own documented example shows `null` here despite the field being marked required and typed as a plain string in the SDK's OpenAPI spec; never observed non-null in this pass (this account has no redeem orders)."""
  status: Literal['DONE', 'PENDING']
  """Settlement status."""


class RedeemOrdersPage(TypedDict):
  """One page of margin credit redeem orders."""

  currentPage: int
  """Current page number."""
  pageSize: int
  """Results per page, as applied."""
  totalNum: int
  """Total matching records."""
  totalPage: int
  """Total number of pages."""
  items: list[RedeemOrder]
  """Redeem orders on this page."""


_Type = RedeemOrdersPage
adapter = validator[_Type](_Type)  # type: ignore


class GetRedeemOrders(RpcEndpoint):
  """`Get Redeem Orders` — mixed into `Credit`, the product exposing `margin.credit.get_redeem_orders`."""

  async def get_redeem_orders(
    self,
    *,
    status: Literal['DONE', 'PENDING'],
    currency: str | None = None,
    redeem_order_no: str | None = None,
    current_page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> RedeemOrdersPage:
    """Page through this account's margin credit redeem orders, filtered by settlement status.

    Args:
      status: Settlement status to filter by.
      currency: Currency to filter by, e.g. `BTC`, `ETH`, `KCS`. Queries every currency if omitted.
      redeem_order_no: Filter by a specific redeem order id.
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
    if redeem_order_no is not None:
      params['redeemOrderNo'] = redeem_order_no
    if current_page is not None:
      params['currentPage'] = current_page
    if page_size is not None:
      params['pageSize'] = page_size
    return await self.authed_request(
      'GET',
      '/api/v3/redeem/orders',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def get_redeem_orders_paged(
    self,
    *,
    status: Literal['DONE', 'PENDING'],
    currency: str | None = None,
    redeem_order_no: str | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[RedeemOrdersPage]:
    """Yield successive pages of `get_redeem_orders`.

    Requests `currentPage` from 1 upwards and stops once it has covered the `totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    current_page = 1
    pages = 0
    while True:
      response = await self.get_redeem_orders(
        status=status,
        currency=currency,
        redeem_order_no=redeem_order_no,
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
