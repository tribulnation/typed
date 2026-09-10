# Paginate Through Results

Endpoints that return a page carry a `_paged` sibling that walks every page automatically, with
no manual cursor bookkeeping. Every `_paged` method is a `PaginatedResponse`: iterate it with
`async for` to get one page of rows at a time (empty pages are skipped), or `await` it to get
every page flattened into one list. To stop early, `break` out of the `async for`.

## Cursor-Paged: Order History

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  async for page in client.uta.trade.order.history_paged(category='SPOT', symbol='BTCUSDT'):
    for order in page:
      print(order['orderId'], order['orderStatus'])

  # Or flatten every page into one list in a single call:
  every_order = await client.uta.trade.order.history_paged(category='SPOT', symbol='BTCUSDT')
```

`history_paged` follows the response's `cursor` and stops once a page carries none. `async for`
yields each page's rows directly, with no `{list, cursor}` envelope to unwrap. `elite_records`,
`move_position_history`, `current_track_orders`/`history_track_orders`/`profit_share_history`
(and their Classic Spot counterparts), `order_fills`, `position_history`,
`virtual_subaccount_list`, `current_followers`/`history_followers`/`profit_details`,
`all_orders`/`my_ads`/`pending_orders`, `sub_transfer_records`, `withdraw_address_book`,
`sub_api_list`, market data's `liquidations`, and UTA's
`financial_records`/`order_fills`/`unfilled_orders` follow the same shape.

The one-shot form returns a single page directly, with its own `cursor` for manual paging:

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  page = await client.uta.trade.order.history(category='SPOT', symbol='BTCUSDT')
```

## Cursor-Paged, Stopping On An Empty Page: Cross Margin Order Fills

A cursor-paged endpoint that stops on an empty page rather than an absent cursor, Classic
Margin's `fills` endpoints, say, has the same shape: each page's rows, one page at a time.

```python
from datetime import datetime, timezone
from typed_bitget import Bitget

async with Bitget.new() as client:
  async for fills in client.classic.margin.cross.order.fills_paged(
    symbol='BTCUSDT', start_time=datetime(2024, 1, 1, tzinfo=timezone.utc),
  ):
    for fill in fills:
      print(fill.get('orderId'), fill.get('tradeId'))
```

## Time-Range Paged: Candles

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

Bitget answers a range it cannot cover in one response with the newest `limit` rows, so
`candles_paged` walks newest first: it keeps your `start_time` fixed and moves `end_time` back
to the oldest candle of each page that came back full, until a page comes back short. Nothing
outside your own `start_time`/`end_time` range is ever requested, and the candle re-served at
each moved bound is dropped, so every candle appears exactly once. Pass `limit` to change the
page size; without it the walk uses the venue's default of 100 rows per page. The seven candle
endpoints (`uta.market.candles.recent`/`history`, `classic.spot.candles`, and
`classic.mix.market.candles.recent`/`history`/`history_mark`/`history_index`) all walk this way.
