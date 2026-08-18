from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class BlockMatchOpenOrder(TypedDict):
  """One open Spot Block Matching order."""

  orderId: NotRequired[str]
  """Order ID."""
  symbol: NotRequired[str]
  """Trading symbol."""
  side: NotRequired[str]
  """Order side."""
  price: NotRequired[str]
  """Order price."""
  amount: NotRequired[str]
  """Order amount."""
  settlementKey: NotRequired[str]
  """Settlement key used to accept this order via `spot.block_match.order_take`."""
  expireTime: NotRequired[int]
  """Millisecond epoch time the order expires."""
  status: NotRequired[str]
  """Order status."""
  createTime: NotRequired[int]
  """Millisecond epoch time the order was created."""


class BlockMatchOpenOrdersPage(TypedDict):
  """A page of the caller's open Spot Block Matching orders."""

  total: NotRequired[int]
  """Total number of matching open orders."""
  rows: NotRequired[list[BlockMatchOpenOrder]]
  """Matching open orders."""


class OpenOrders(RpcEndpoint):
  """Query the caller's open Spot Block Matching orders."""

  async def open_orders(
    self,
    *,
    page: int,
    rows: int,
    validate: bool | None = None,
  ) -> BlockMatchOpenOrdersPage:
    """Query the caller's open Spot Block Matching orders.

    Args:
      page: Page number, starting from 1.
      rows: Number of records to query.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-spot-block-matching/api/rest-api/~#query-open-order)
    """
    params: dict = {
      'page': page,
      'rows': rows,
    }
    _Response = BlockMatchOpenOrdersPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/block-match/order/query-open-order',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def open_orders_paged(
    self,
    *,
    rows: int,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[BlockMatchOpenOrdersPage]:
    """Yield successive pages of `open_orders`.

    Requests `page` from 1 upwards and stops once it has covered the `total` items the
    response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.open_orders(rows=rows, page=page, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or pages * rows >= total:
        break
      page += 1
