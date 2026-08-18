from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from mexc.core import Timestamp, timestamp as ts, validator
from mexc.futures.core import AuthFuturesMixin

class HistoryOrdersItem(TypedDict):
  """Futures order record."""
  orderId: int | str
  """Order identifier."""
  symbol: str
  """Contract symbol."""
  positionId: int | str
  """Related position identifier."""
  price: float
  """Order or trigger price."""
  vol: float
  """Order volume."""
  leverage: int
  """Leverage used by the order."""
  side: Literal[1, 2, 3, 4]
  """Order side: 1 open long, 2 close short, 3 open short, 4 close long."""
  category: Literal[1, 2, 3, 4]
  """Order category: 1 limit order, 2 system take-over delegate, 3 close delegate, 4 ADL reduction."""
  orderType: Literal[1, 2, 3, 4, 5, 6]
  """Order type: 1 limit, 2 post-only maker, 3 IOC, 4 FOK, 5 market, 6 market-to-current-price."""
  dealAvgPrice: float
  """Average filled price."""
  dealVol: float
  """Filled volume."""
  orderMargin: float
  """Margin reserved for the order."""
  takerFee: float
  """Taker fee."""
  makerFee: float
  """Maker fee."""
  profit: float
  """Realized close profit."""
  feeCurrency: str
  """Fee currency."""
  openType: Literal[1, 2]
  """Margin mode: 1 isolated, 2 cross."""
  state: Literal[1, 2, 3, 4, 5]
  """Order state: 1 uninformed, 2 uncompleted, 3 completed, 4 cancelled, 5 invalid."""
  externalOid: str
  """Client-provided external order id."""
  errorCode: int
  """Order error code."""
  usedMargin: float
  """Used margin."""
  createTime: int | str
  """Creation time."""
  updateTime: int | str
  """Last update time."""
  stopLossPrice: NotRequired[float]
  """Attached stop-loss price when present."""
  takeProfitPrice: NotRequired[float]
  """Attached take-profit price when present."""

class HistoryOrdersResponse(TypedDict):
  """Get historical futures orders response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[list[HistoryOrdersItem]]
  """Historical futures orders."""

adapter = validator(HistoryOrdersResponse)

class HistoryOrders(AuthFuturesMixin):
  async def history_orders(
    self, *,
    symbol: str | None = None, states: str | None = None,
    category: Literal[1, 2, 3, 4] | None = None,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    side: Literal[1, 2, 3, 4] | None = None, page_num: int, page_size: int,
    validate: bool | None = None,
  ) -> HistoryOrdersResponse:
    """Returns paginated historical futures orders for the signed account.

    Args:
      symbol: Optional contract symbol filter.
      states: Comma-separated order states.
      category: Order category filter: 1 limit order, 2 system take-over delegate, 3 close delegate, 4 ADL reduction.
      start_time: Start time in milliseconds; maximum 90-day span with end_time.
      end_time: End time in milliseconds; maximum 90-day span with start_time.
      side: Order side filter: 1 open long, 2 close short, 3 open short, 4 close long.
      page_num: Page number; default is 1.
      page_size: Page size; default 20, maximum 100.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-all-of-the-user-39-s-historical-orders)
    """
    headers = {}
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if states is not None:
      params['states'] = states
    if category is not None:
      params['category'] = category
    if start_time is not None:
      params['start_time'] = ts.dump(start_time)
    if end_time is not None:
      params['end_time'] = ts.dump(end_time)
    if side is not None:
      params['side'] = side
    if page_num is not None:
      params['page_num'] = page_num
    if page_size is not None:
      params['page_size'] = page_size
    r = await self.signed_request('GET', '/api/v1/private/order/list/history_orders', params=params or None, headers=headers)
    return self.envelope_output(r.text, adapter, validate)

  async def history_orders_paged(
    self, *,
    symbol: str | None = None, states: str | None = None,
    category: Literal[1, 2, 3, 4] | None = None,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    side: Literal[1, 2, 3, 4] | None = None, page_size: int,
    max_pages: int | None = None, validate: bool | None = None,
  ) -> AsyncIterator[HistoryOrdersResponse]:
    """Yield successive pages of `history_orders`.

    Requests `page_num` from 1 upwards and stops on the first page shorter than
    `page_size`, or after `max_pages` pages when one is given.
    """
    page_num = 1
    pages = 0
    while True:
      response = await self.history_orders(symbol=symbol, states=states, category=category, start_time=start_time, end_time=end_time, side=side, page_size=page_size, page_num=page_num, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('data') if response is not None else None
      if not rows or len(rows) < page_size:
        break
      page_num += 1
