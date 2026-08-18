from typing_extensions import AsyncIterator, Literal, NotRequired, TypedDict
from typed_core.validation import validator
from binance.core import Timestamp, timestamp
from binance.core.endpoint.rpc import RpcEndpoint


class EquityTradeHistoryRow(TypedDict):
  """One trade execution (fill) in the caller's equity trade history."""

  executionId: NotRequired[str]
  """Execution (per-fill) id."""
  orderId: NotRequired[str]
  """The owning order's id."""
  symbol: NotRequired[str]
  """US-equity ticker."""
  quote: NotRequired[str]
  """Quote asset."""
  side: NotRequired[Literal['BUY', 'SELL']]
  """Order side."""
  orderType: NotRequired[Literal['MARKET', 'LIMIT']]
  """Order type."""
  price: NotRequired[str]
  """Execution price (USD)."""
  qty: NotRequired[str]
  """Executed quantity."""
  fee: NotRequired[str]
  """Commission fee for this execution (USD)."""
  total: NotRequired[str]
  """Notional of this execution (`qty x price`)."""
  executionAt: NotRequired[Timestamp]
  """Execution time."""
  updatedAt: NotRequired[Timestamp]
  """Last update time."""


class EquityTradeHistoryPage(TypedDict):
  """One page of equity trade (per-fill) history."""

  total: NotRequired[int]
  """Total number of rows matching the filter."""
  page: NotRequired[int]
  """Current page."""
  size: NotRequired[int]
  """Current page size."""
  rows: NotRequired[list[EquityTradeHistoryRow]]
  """Trade rows on this page. Empty when nothing matches."""


class TradeHistory(RpcEndpoint):
  """Paged equity trade (per-fill) history for the caller. Each row is one execution, not one order -- a partially filled order produces multiple rows. Filters by symbol, side, specific `orderId`, and time range."""

  async def trade_history(
    self,
    *,
    symbol: str | None = None,
    side: Literal['BUY', 'SELL'] | None = None,
    order_id: str | None = None,
    start_time: Timestamp,
    end_time: Timestamp,
    current: int | None = None,
    size: int | None = None,
    validate: bool | None = None,
  ) -> EquityTradeHistoryPage:
    """Paged equity trade (per-fill) history for the caller. Each row is one execution, not one order -- a partially filled order produces multiple rows. Filters by symbol, side, specific `orderId`, and time range.

    Args:
      symbol: US-equity ticker filter, e.g. `NVDA`.
      side: Side filter.
      order_id: Narrow the result to executions of a single order.
      start_time: Start time.
      end_time: End time.
      current: Page number, 1-based.
      size: Page size. Default `20`, max `100`.

    References:
      - [Official docs](https://developers.binance.com/en/docs/catalog/advanced-trading-stocks-trading/api/rest-api/trade#equity-trade-history)
    """
    params: dict = {
      'startTime': timestamp.dump(start_time),
      'endTime': timestamp.dump(end_time),
    }
    if symbol is not None:
      params['symbol'] = symbol
    if side is not None:
      params['side'] = side
    if order_id is not None:
      params['orderId'] = order_id
    if current is not None:
      params['current'] = current
    if size is not None:
      params['size'] = size
    _Response = EquityTradeHistoryPage
    _validator = validator[_Response](_Response)
    return await self.authed_request(
      'GET',
      '/sapi/v1/equity/trade/history',
      params=params,
      validator=_validator,
      validate=validate,
    )

  async def trade_history_paged(
    self,
    *,
    symbol: str | None = None,
    side: Literal['BUY', 'SELL'] | None = None,
    order_id: str | None = None,
    start_time: Timestamp,
    end_time: Timestamp,
    size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[EquityTradeHistoryPage]:
    """Yield successive pages of `trade_history`.

    Requests `current` from 1 upwards and stops once it has covered the `total` items
    the response reports, or after `max_pages` pages when one is given.
    """
    current = 1
    pages = 0
    while True:
      response = await self.trade_history(
        symbol=symbol,
        side=side,
        order_id=order_id,
        start_time=start_time,
        end_time=end_time,
        size=size,
        current=current,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      total = response.get('total') if response is not None else None
      total = int(total) if total is not None else None
      if total is None or size is None or pages * size >= total:
        break
      current += 1
