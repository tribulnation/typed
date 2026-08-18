from mexc.core import Timestamp, timestamp as ts, validator
from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from mexc.futures.core import AuthFuturesMixin

class StopOrdersItem(TypedDict):
  """Stop-limit order record."""
  id: int | str
  """Stop-limit order id."""
  orderId: int | str
  """Limit order id, or zero if based on a position."""
  symbol: str
  """Contract symbol."""
  positionId: int | str
  """Position id."""
  stopLossPrice: float
  """Stop-loss price."""
  takeProfitPrice: float
  """Take-profit price."""
  state: Literal[1, 2, 3, 4, 5]
  """Stop-limit order state: 1 untriggered, 2 cancelled, 3 executed, 4 invalid, 5 execution failed."""
  triggerSide: int
  """Trigger side."""
  positionType: Literal[1, 2]
  """Position side: 1 long, 2 short."""
  vol: float
  """Configured volume."""
  realityVol: float
  """Actual executed volume."""
  placeOrderId: int | str
  """Placed order id."""
  errorCode: int
  """Error code."""
  version: int
  """Record version."""
  isFinished: int
  """Final-state indicator."""
  createTime: int | str
  """Creation time."""
  updateTime: int | str
  """Update time."""

class StopOrdersResponse(TypedDict):
  """List futures stop-limit orders response envelope."""
  success: bool
  """Whether the API request succeeded."""
  code: NotRequired[int]
  """MEXC response code; zero indicates success when present."""
  message: NotRequired[str]
  """Error or status message when present."""
  data: NotRequired[list[StopOrdersItem]]
  """Stop-limit order records."""

adapter = validator(StopOrdersResponse)

class StopOrders(AuthFuturesMixin):
  async def stop_orders(
    self, *,
    symbol: str | None = None, is_finished: int | None = None,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    page_num: int, page_size: int, validate: bool | None = None,
  ) -> StopOrdersResponse:
    """Returns paginated stop-limit trigger orders for the signed futures account.

    Args:
      symbol: Optional contract symbol filter.
      is_finished: Final-state filter: 0 unfinished, 1 finished.
      start_time: Start time in milliseconds; maximum span is 90 days.
      end_time: End time in milliseconds; maximum span is 90 days.
      page_num: Page number; default is 1.
      page_size: Page size; default 20, maximum 100.
      validate: Validation override for this request.

    Returns:
      The validated endpoint response.

    References:
      - [MEXC API docs](https://mexcdevelop.github.io/apidocs/contract_v1_en/#get-the-stop-limit-order-list)
    """
    headers = {}
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if is_finished is not None:
      params['is_finished'] = is_finished
    if start_time is not None:
      params['start_time'] = ts.dump(start_time)
    if end_time is not None:
      params['end_time'] = ts.dump(end_time)
    if page_num is not None:
      params['page_num'] = page_num
    if page_size is not None:
      params['page_size'] = page_size
    r = await self.signed_request('GET', '/api/v1/private/stoporder/list/orders', params=params or None, headers=headers)
    return self.envelope_output(r.text, adapter, validate)

  async def stop_orders_paged(
    self, *,
    symbol: str | None = None, is_finished: int | None = None,
    start_time: Timestamp | None = None, end_time: Timestamp | None = None,
    page_size: int, max_pages: int | None = None, validate: bool | None = None,
  ) -> AsyncIterator[StopOrdersResponse]:
    """Yield successive pages of `stop_orders`.

    Requests `page_num` from 1 upwards and stops on the first page shorter than
    `page_size`, or after `max_pages` pages when one is given.
    """
    page_num = 1
    pages = 0
    while True:
      response = await self.stop_orders(symbol=symbol, is_finished=is_finished, start_time=start_time, end_time=end_time, page_size=page_size, page_num=page_num, validate=validate)
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      rows = response.get('data') if response is not None else None
      if not rows or len(rows) < page_size:
        break
      page_num += 1
