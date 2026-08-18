"""`GET /api/v3/hf/margin/fills` — Get Trade History."""

from typing_extensions import AsyncIterator, Literal
from typed_core.validation import TypedDict, validator
from kucoin.core import RpcEndpoint, Timestamp, timestamp


class HfMarginFill(TypedDict):
  """A single margin hf trade fill."""

  id: int
  """Fill record id."""
  symbol: str
  """Trading pair symbol."""
  tradeId: int
  """Unique trade id."""
  orderId: str
  """Id of this account's order that this fill belongs to."""
  counterOrderId: str
  """Id of the matched counter-order."""
  side: Literal['buy', 'sell']
  """Order side."""
  liquidity: Literal['taker', 'maker']
  """Whether this account's order added or removed liquidity."""
  forceTaker: bool
  """Whether the order was forced to take (e.g. a market order)."""
  price: str
  """Execution price."""
  size: str
  """Quantity filled."""
  funds: str
  """Value of the fill, in the trading pair's quote currency."""
  fee: str
  """Trading fee charged for this fill."""
  feeRate: str
  """Trading fee rate applied."""
  feeCurrency: str
  """Currency the trading fee is charged in."""
  stop: str
  """Stop-order type this fill originated from, or an empty string when the fill did not originate from a stop order."""
  tradeType: str
  """Margin trade classification. KuCoin's examples show `MARGIN_TRADE` (cross); this endpoint's docs page never states the field is a closed set, so it is left as a plain string rather than a guessed enum."""
  taxRate: str
  """Tax rate applied."""
  tax: str
  """Tax amount charged."""
  type: Literal['limit', 'market']
  """Order type."""
  createdAt: Timestamp
  """Time the fill occurred."""


class HfMarginFillsPage(TypedDict):
  """Page of margin hf trade fills."""

  items: list[HfMarginFill]
  """Trade fills on this page, newest first."""
  lastId: int
  """Cursor to pass as `lastId` to fetch the next older page. `0` when there is no further page."""


_Type = HfMarginFillsPage
adapter = validator[_Type](_Type)  # type: ignore


class GetTradeHistory(RpcEndpoint):
  """`Get Trade History` — mixed into `OrdersHf`, the product exposing `margin.orders_hf.get_trade_history`."""

  async def get_trade_history(
    self,
    *,
    symbol: str,
    trade_type: str,
    order_id: str | None = None,
    side: Literal['buy', 'sell'] | None = None,
    type: Literal['limit', 'market'] | None = None,
    last_id: int | None = None,
    limit: int | None = None,
    start_at: Timestamp | None = None,
    end_at: Timestamp | None = None,
    validate: bool | None = None,
  ) -> HfMarginFillsPage:
    """Cursor-paginated list of the authenticated account's margin hf trade fills, for one trading pair and margin mode. Data is retained for up to 3 months; each query window is capped at 7 days.

    Args:
      symbol: Trading pair symbol to filter by.
      trade_type: Margin mode to look up. Confirmed live 2026-08-08: both `MARGIN_TRADE` (cross) and `MARGIN_ISOLATED_TRADE` (isolated) are accepted, but this endpoint's docs page never states the field is a closed set, so it is left as a plain string rather than a guessed enum.
      order_id: Order id to filter by.
      side: Order side to filter by.
      type: Order type to filter by.
      last_id: Cursor from a previous page's `lastId`, to fetch the next older page.
      limit: Results per page.
      start_at: Start of the time range, inclusive.
      end_at: End of the time range, inclusive.
      validate: Validate the response against the generated schema.

    References:
      - [KuCoin API docs](https://www.kucoin.com/docs-new)
    """
    params: dict = {
      'symbol': symbol,
      'tradeType': trade_type,
    }
    if order_id is not None:
      params['orderId'] = order_id
    if side is not None:
      params['side'] = side
    if type is not None:
      params['type'] = type
    if last_id is not None:
      params['lastId'] = last_id
    if limit is not None:
      params['limit'] = limit
    if start_at is not None:
      params['startAt'] = timestamp.dump(start_at)
    if end_at is not None:
      params['endAt'] = timestamp.dump(end_at)
    return await self.authed_request(
      'GET',
      '/api/v3/hf/margin/fills',
      params=params,
      validator=adapter,
      validate=validate,
    )

  async def get_trade_history_paged(
    self,
    *,
    symbol: str,
    trade_type: str,
    order_id: str | None = None,
    side: Literal['buy', 'sell'] | None = None,
    type: Literal['limit', 'market'] | None = None,
    limit: int | None = None,
    start_at: Timestamp | None = None,
    end_at: Timestamp | None = None,
    max_pages: int | None = None,
    validate: bool | None = None,
  ) -> AsyncIterator[HfMarginFillsPage]:
    """Yield successive pages of `get_trade_history`.

    Passes each page's token back as `lastId` and stops when a response carries no
    `lastId`, or after `max_pages` pages when one is given.
    """
    last_id: int | None = None
    pages = 0
    while True:
      response = await self.get_trade_history(
        symbol=symbol,
        trade_type=trade_type,
        order_id=order_id,
        side=side,
        type=type,
        limit=limit,
        start_at=start_at,
        end_at=end_at,
        last_id=last_id,
        validate=validate,
      )
      yield response
      pages += 1
      if max_pages is not None and pages >= max_pages:
        break
      last_id = response.get('lastId') if response is not None else None
      if not last_id:
        break
