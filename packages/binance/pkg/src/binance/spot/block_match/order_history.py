from typing_extensions import AsyncIterator, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core.endpoint.rpc import RpcEndpoint


class BlockMatchOrderHistoryEntry(TypedDict):
  """One Spot Block Matching order history entry."""

  orderId: NotRequired[str]
  """Order ID."""
  role: NotRequired[str]
  """Caller's role in the trade."""
  symbol: NotRequired[str]
  """Trading symbol."""
  side: NotRequired[str]
  """Order side."""
  price: NotRequired[str]
  """Order price."""
  amount: NotRequired[str]
  """Order amount."""
  fee: NotRequired[str]
  """Trading fee charged."""
  expireTime: NotRequired[int]
  """Millisecond epoch time the order expires."""
  status: NotRequired[str]
  """Order status."""
  createTime: NotRequired[int]
  """Millisecond epoch time the order was created."""


class BlockMatchOrderHistoryPage(TypedDict):
  """A page of the caller's Spot Block Matching order history."""

  total: NotRequired[int]
  """Total number of matching order history entries."""
  rows: NotRequired[list[BlockMatchOrderHistoryEntry]]
  """Matching order history entries."""


class OrderHistory(RpcEndpoint):
  """Query the caller's Spot Block Matching order history."""

  async def order_history(
    self,
    *,
    start_time: int,
    end_time: int,
    page: int,
    rows: int,
    validate: bool | None = None,
  ) -> BlockMatchOrderHistoryPage:
    """Query the caller's Spot Block Matching order history.

    Args:
      start_time: Start time in milliseconds.
      end_time: End time in milliseconds.
      page: Page number, starting from 1.
      rows: Number of records to query.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/vip-and-institutional-spot-block-matching/api/rest-api/~#query-order-history)
    """
    params: dict = {
      'startTime': start_time,
      'endTime': end_time,
      'page': page,
      'rows': rows,
    }
    _Response = BlockMatchOrderHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/block-match/order/query-order-history',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def order_history_paged(
    self,
    *,
    start_time: int,
    end_time: int,
    rows: int,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[BlockMatchOrderHistoryPage]:
    """Yield successive pages of `order_history`.

    Requests `page` from 1 upwards and stops once it has covered the `total` items the
    response reports, or after `max_pages` pages when one is given.
    """
    page = 1
    pages = 0
    while True:
      response = await self.order_history(
        start_time=start_time,
        end_time=end_time,
        rows=rows,
        page=page,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or pages * rows >= total:
        break
      page += 1
