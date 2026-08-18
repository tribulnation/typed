"""`GET /api/v3/hf/margin/stop-orders` — Get Stop Orders List."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp, timestamp


class MarginStopOrder(TypedDict):
  id: str
  """Stop order id."""
  symbol: str
  """Trading pair."""
  userId: str
  """Owning account's user id."""
  status: Literal['NEW', 'TRIGGERED']
  """Stop order status. Carried over from Spot's confirmed `StopOrder.status` enum -- not independently confirmed by this endpoint's own docs prose, only its example (`NEW`)."""
  type: Literal['limit', 'market']
  """Order type submitted once the stop triggers."""
  side: Literal['buy', 'sell']
  """Order side."""
  price: str
  """Limit price for the order submitted once the stop triggers."""
  size: str
  """Order quantity, in the base currency."""
  funds: str | None
  """Order value in the quote currency, for a `market`-type triggered order; `null` for `limit`."""
  stp: Literal['CN', 'CO', 'CB', 'DC'] | None
  """Self-trade prevention strategy in effect, or `null` when none was requested."""
  timeInForce: Literal['GTC', 'GTT', 'IOC', 'FOK']
  """Time-in-force rule for the order submitted once the stop triggers."""
  cancelAfter: int
  """Seconds until the triggered order is automatically cancelled when `timeInForce` is `GTT`; `-1` means never."""
  postOnly: bool
  """Whether the triggered order is post-only."""
  hidden: bool
  """Whether the triggered order would be hidden from the order book. KuCoin discontinued Hidden Orders as of 2026-08-03; this remains a response field but is no longer a settable request parameter."""
  iceberg: bool
  """Whether the triggered order would be an iceberg order. Discontinued as a request parameter as of 2026-08-03; see `hidden`."""
  visibleSize: str | None
  """Visible portion of an iceberg order once triggered; `null` since Hidden Orders were discontinued."""
  channel: str
  """Order submission channel, e.g. `API`."""
  clientOid: str
  """Caller-assigned order id passed at creation time."""
  remark: str
  """Order remark passed at creation time."""
  tags: str | None
  """Order source tag, or `null` when none applies."""
  relatedNo: str | None
  """Related order id, if this stop order is linked to another order; `null` otherwise. Undocumented by KuCoin beyond the field name."""
  orderTime: int
  """Time the stop order was placed, accurate to nanoseconds."""
  domainId: str
  """Originating domain, e.g. `kucoin`."""
  tradeSource: str
  """Who placed the order. Not independently confirmed as a closed set on this endpoint's own docs page (Spot's parallel field is), so left bare."""
  tradeType: str
  """Margin mode the order was placed on. Not stated as a closed set on this endpoint's docs page, matching `margin.orders_hf`'s identical treatment of the same field."""
  feeCurrency: str
  """Currency the trading fee is charged in."""
  takerFeeRate: str
  """Taker fee rate applied to this order."""
  makerFeeRate: str
  """Maker fee rate applied to this order."""
  createdAt: Timestamp
  """Time the stop order was created."""
  stop: Literal['loss', 'entry']
  """Stop order trigger type."""
  stopTriggerTime: Timestamp | None
  """Time the stop condition triggered; `null` while the order is still `NEW`."""
  stopPrice: str
  """Trigger price."""
  limitPrice: str | None
  """Undocumented by KuCoin beyond the field name, carried over from Spot's identically-named, identically-undocumented field."""
  pop: str | None
  """Undocumented by KuCoin beyond the field name, carried over from Spot's identically-named, identically-undocumented field."""
  activateCondition: str | None
  """Undocumented by KuCoin beyond the field name, carried over from Spot's identically-named, identically-undocumented field."""


class MarginStopOrdersPage(TypedDict):
  currentPage: int
  """Page number returned."""
  pageSize: int
  """Results per page."""
  totalNum: int
  """Total number of orders matching the filters."""
  totalPage: int
  """Total number of pages."""
  items: list[MarginStopOrder]
  """Margin stop orders on this page."""


_Type = MarginStopOrdersPage
adapter = validator[_Type](_Type)  # type: ignore


class GetList(RpcEndpoint):
  """`Get Stop Orders List` — mixed into `StopOrders`, the product exposing `margin.stop_orders.get_list`."""

  async def get_list(
    self,
    *,
    symbol: str | None = None,
    side: Literal['buy', 'sell'] | None = None,
    type: Literal['limit', 'market'] | None = None,
    trade_type: str | None = None,
    start_at: Timestamp | None = None,
    end_at: Timestamp | None = None,
    order_ids: str | None = None,
    stop: Literal['loss', 'entry'] | None = None,
    current_page: int | None = None,
    page_size: int | None = None,
    validate: bool | None = None,
  ) -> MarginStopOrdersPage:
    """Get a paginated list of this account's untriggered margin stop orders, sorted most recent first.

    Args:
      symbol: Only list orders for this trading pair.
      side: Only list orders on this side.
      type: Only list orders of this type.
      trade_type: Only list orders on this margin mode. Confirmed live 2026-08-09: both `MARGIN_TRADE` (cross) and `MARGIN_ISOLATED_TRADE` (isolated) are accepted, but this endpoint's docs page never states the field is a closed set, so it is left as a plain string rather than a guessed enum, matching `margin.orders_hf.get_open_orders`'s identical treatment.
      start_at: Only list orders created at or after this time.
      end_at: Only list orders created at or before this time.
      order_ids: Comma-separated stop order ids to narrow the list to.
      stop: Only list orders of this trigger type. Unlike Spot's identically-named list filter (which selects between the stop and OCO order *families*, since Spot shares one list endpoint between them), this margin endpoint has a wholly separate `margin.oco_orders.get_list` endpoint -- so this `stop` filter instead means each order's own trigger type, the same concept as the item-level `stop` field below.
      current_page: Page number to fetch, starting at 1.
      page_size: Results per page. Live-confirmed default 20 2026-08-09 -- not independently confirmed against any documented default, since this endpoint's docs page states none.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params = {}
    if symbol is not None:
      params['symbol'] = symbol
    if side is not None:
      params['side'] = side
    if type is not None:
      params['type'] = type
    if trade_type is not None:
      params['tradeType'] = trade_type
    if start_at is not None:
      params['startAt'] = timestamp.dump(start_at)
    if end_at is not None:
      params['endAt'] = timestamp.dump(end_at)
    if order_ids is not None:
      params['orderIds'] = order_ids
    if stop is not None:
      params['stop'] = stop
    if current_page is not None:
      params['currentPage'] = current_page
    if page_size is not None:
      params['pageSize'] = page_size
    return await self.authed_request(
      'GET',
      '/api/v3/hf/margin/stop-orders',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def get_list_paged(
    self,
    *,
    symbol: str | None = None,
    side: Literal['buy', 'sell'] | None = None,
    type: Literal['limit', 'market'] | None = None,
    trade_type: str | None = None,
    start_at: Timestamp | None = None,
    end_at: Timestamp | None = None,
    order_ids: str | None = None,
    stop: Literal['loss', 'entry'] | None = None,
    page_size: int | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[MarginStopOrdersPage]:
    """Yield successive pages of `get_list`.

    Requests `currentPage` from 1 upwards and stops once it has covered the `totalPage`
    pages the response reports, or after `max_pages` pages when one is given.
    """
    current_page = 1
    pages = 0
    while True:
      response = await self.get_list(
        symbol=symbol,
        side=side,
        type=type,
        trade_type=trade_type,
        start_at=start_at,
        end_at=end_at,
        order_ids=order_ids,
        stop=stop,
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
