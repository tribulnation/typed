# Paginate Through Results

Endpoints that return a page carry a `_paged` sibling that walks every page automatically, with
no manual cursor bookkeeping. Most of these are a plain async iterator; a cursor-paged endpoint
whose response is just `{rows, cursor}` -- nothing else worth keeping per page -- is instead
`PaginatedResponse`-shaped: usable both as `async for` (one page of rows at a time) and as a
single `await` (every page flattened into one list).

## Cursor-Paged, `PaginatedResponse`-Shaped: Order History

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  async for page in client.uta.trade.order.history_paged(category='SPOT', symbol='BTCUSDT'):
    for order in page:
      print(order['orderId'], order['orderStatus'])

  # Or flatten every page into one list in a single call:
  every_order = await client.uta.trade.order.history_paged(category='SPOT', symbol='BTCUSDT')
```

`history_orders_paged` follows the response's `cursor` and stops once a page carries none --
`async for` yields each page's rows directly (no `{list, cursor}` envelope to unwrap), and
`await` walks every page for you. `elite_records`, `move_position_history`,
`current_track_orders`/`history_track_orders`/`profit_share_history` (and their Classic Spot
counterparts), `order_fills`, `position_history`, `virtual_subaccount_list`,
`current_followers`/`history_followers`/`profit_details`, `all_orders`/`my_ads`/`pending_orders`,
`sub_transfer_records`, `withdraw_address_book`, `sub_api_list`, market data's `liquidations`,
and UTA's `financial_records`/`order_fills`/`unfilled_orders` follow the same shape.

The one-shot form returns a single page directly, with its own `cursor` for manual paging:

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  page = await client.uta.trade.order.history(category='SPOT', symbol='BTCUSDT')
```

## Cursor-Paged, Plain Async Iterator: Cross Margin Order Fills

A cursor-paged endpoint that stops on an empty page, rather than an absent cursor -- Classic
Margin's `fills` endpoints, say -- stays a plain async iterator instead, yielding the whole
response per page:

```python
from datetime import datetime, timezone
from typed_bitget import Bitget

async with Bitget.new() as client:
  async for page in client.classic.margin.cross.order.fills_paged(
    symbol='BTCUSDT', start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
  ):
    for fill in page['fills']:
      print(fill.get('orderId'), fill.get('tradeId'))
```

Pass `max_pages` to cap how many pages a plain async-iterator `_paged` method walks -- unlike the
`PaginatedResponse`-shaped form above, which has no such parameter.

## Window-Paged: Candles

```python
from datetime import datetime, timezone
from typed_bitget import Bitget

async with Bitget.new(public=True) as client:
  async for page in client.uta.market.candles.recent_paged(
    category='SPOT', symbol='BTCUSDT', interval='1m',
    start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
    end_time=datetime(2024, 1, 2, tzinfo=timezone.utc),
  ):
    print(page)
```

`candles_paged` walks the `start_time` to `end_time` window backwards by its own width and stops
on the first empty window. A page that comes back full (as many rows as requested) may be
hiding more candles the venue truncated. In that case `candles_paged` raises `LogicError`
rather than silently skipping rows; pass `allow_truncation=True` to accept the loss and
continue.
