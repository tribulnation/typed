"""`GET /api/v1/fills` — Get Trade History."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.types import FuturesTrade
from kucoin.core import RpcEndpoint


class FuturesTradePage(TypedDict):
  """One page of fills."""

  currentPage: int
  """Current page number."""
  pageSize: int
  """Results per page, as requested."""
  totalNum: int
  """Total matching fills."""
  totalPage: int
  """Total number of pages."""
  items: list[FuturesTrade]
  """Fills on this page."""


_Type = FuturesTradePage
adapter = validator[_Type](_Type)  # type: ignore


class GetTradeHistory(RpcEndpoint):
  """`Get Trade History` — mixed into `Orders`, the product exposing `futures.orders.get_trade_history`."""

  async def get_trade_history(
    self,
    *,
    order_id: str | None = None,
    symbol: str | None = None,
    side: Literal['buy', 'sell'] | None = None,
    type: Literal['limit', 'market', 'limit_stop', 'market_stop'] | None = None,
    trade_types: str | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    current_page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> FuturesTradePage:
    """List this account's own fills, up to a 3-month retention window; each query is further limited to a 7-day `startAt`/`endAt` range. Get Recent Trade History is the lower-latency alternative for the last 24 hours.

    Args:
      order_id: Restrict to fills of one order; other filters are ignored when this is set.
      symbol: Contract symbol to filter by.
      side: Order side to filter by.
      type: Order type to filter by.
      trade_types: Comma-separated trade type(s) to filter by, e.g. `trade` or `adl,liquid`. Queries every type when omitted. Not specced as an `enum` since it is a free-form comma-joined list rather than a single closed value -- see `FuturesTrade.tradeType` (spec/schemas.json) for the individual values KuCoin documents.
      start_at: Start of the time window, Unix milliseconds. Defaults to 24 hours before `endAt` when omitted.
      end_at: End of the time window, Unix milliseconds. Defaults to 24 hours after `startAt` when omitted.
      current_page: Page number.
      page_size: Results per page.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if order_id is not None:
      params['orderId'] = order_id
    if symbol is not None:
      params['symbol'] = symbol
    if side is not None:
      params['side'] = side
    if type is not None:
      params['type'] = type
    if trade_types is not None:
      params['tradeTypes'] = trade_types
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
      '/api/v1/fills',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def get_trade_history_paged(
    self,
    *,
    order_id: str | None = None,
    symbol: str | None = None,
    side: Literal['buy', 'sell'] | None = None,
    type: Literal['limit', 'market', 'limit_stop', 'market_stop'] | None = None,
    trade_types: str | None = None,
    start_at: int | None = None,
    end_at: int | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[FuturesTradePage]:
    """Yield successive pages of `get_trade_history`.

    Requests `currentPage` from 1 upwards and stops once it has covered the `totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    current_page = 1
    pages = 0
    while True:
      response = await self.get_trade_history(
        order_id=order_id,
        symbol=symbol,
        side=side,
        type=type,
        trade_types=trade_types,
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
