"""`GET /api/v1/convert/limit/orders` — Get Convert Limit Orders."""

from typing_extensions import AsyncIterator
from typed_core.validation import TypedDict, validator
from kucoin.types import ConvertLimitOrder
from kucoin.core import RpcEndpoint


class ConvertLimitOrdersPage(TypedDict):
  """One page of convert limit orders."""

  currentPage: int
  """Current page number."""
  pageSize: int
  """Results per page, as applied."""
  totalNum: int
  """Total matching records."""
  totalPage: int
  """Total number of pages."""
  items: list[ConvertLimitOrder]
  """Orders on this page, most recent first."""


_Type = ConvertLimitOrdersPage
adapter = validator[_Type](_Type)  # type: ignore


class LimitOrders(RpcEndpoint):
  """`Get Convert Limit Orders` — mixed into `Convert`, the product exposing `convert.limit_orders`."""

  async def limit_orders(
    self,
    *,
    start_at: int | None = None,
    end_at: int | None = None,
    page: int | None = None,
    page_size: int | None = None,
    status: str | None = None,
    validate: bool | None = None,
  ) -> ConvertLimitOrdersPage:
    """Page through this account's convert limit orders.

    Args:
      start_at: Restrict to orders placed at or after this Unix millisecond timestamp.
      end_at: Restrict to orders placed at or before this Unix millisecond timestamp.
      page: Page number.
      page_size: Results per page. Confirmed live the same range as the sibling Get Convert Order History: [20, 100]; 10 rejects with `400100 'pageSize not in range value'`.
      status: Restrict to one order status, for example `CANCELLED`. KuCoin does not publish a closed set for this field, so it's left as a plain string rather than a guessed enum.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if start_at is not None:
      params['startAt'] = start_at
    if end_at is not None:
      params['endAt'] = end_at
    if page is not None:
      params['page'] = page
    if page_size is not None:
      params['pageSize'] = page_size
    if status is not None:
      params['status'] = status
    return await self.authed_request(
      'GET',
      '/api/v1/convert/limit/orders',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def limit_orders_paged(
    self,
    *,
    start_at: int | None = None,
    end_at: int | None = None,
    page_size: int | None = None,
    status: str | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[ConvertLimitOrdersPage]:
    """Yield successive pages of `limit_orders`.

    Requests `page` from 1 upwards and stops once it has covered the `totalPage` pages
    the response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.limit_orders(
        start_at=start_at,
        end_at=end_at,
        page_size=page_size,
        status=status,
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
