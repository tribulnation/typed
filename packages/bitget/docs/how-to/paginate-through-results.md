# Paginate Through Results

Endpoints that return a page carry a `_paged` sibling that walks every page automatically as an
async iterator, with no manual cursor bookkeeping.

## Cursor-Paged: Order History

```python
from bitget import Bitget

async with Bitget.new() as client:
  async for page in client.uta.trade.history_orders_paged(category='SPOT', symbol='BTCUSDT'):
    for order in page['list']:
      print(order['orderId'], order['orderStatus'])
```

`history_orders_paged` follows the response's `cursor` and stops once a page carries none. Pass
`max_pages` to cap how many pages it walks.

The one-shot form returns a single page directly, with its own `cursor` for manual paging:

```python
from bitget import Bitget

async with Bitget.new() as client:
  page = await client.uta.trade.history_orders(category='SPOT', symbol='BTCUSDT')
```

`financial_records`, `fills`, `unfilled_orders`, and `elite_records` follow the same
cursor-paged shape.

## Window-Paged: Candles

```python
from datetime import datetime, timezone
from bitget import Bitget

async with Bitget.new(public=True) as client:
  async for page in client.uta.market.candles_paged(
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
