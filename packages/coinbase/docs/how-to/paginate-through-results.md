# Paginate Through Results

A paged endpoint has two forms on the same method: call it directly for one page, or its
pager sibling for every page. Every pager returns a `PaginatedResponse`: `await` it to
flatten every page into one list, or `async for` it to walk one page (a list of rows) at a
time. Either way it stops on its own, so there is nothing to cap. To stop early, `break`
out of the `async for`.

Cursor-paginated pagers stop once the venue stops returning a next cursor. `products.candles`
(and `products.public.candles`) is a time-range walk instead: Coinbase keeps the newest
candles when a range holds more than `limit`, so the pager moves `end` back to the earliest
candle of each full page, never before your own `start`, and stops on the first page shorter
than `limit` (300 by default: a spot product serves up to 350 candles per request but an
INTX perpetual such as `BTC-PERP-INTX` serves at most 300, and the pager is sized so neither
loses rows). Pages arrive newest first; reverse the flattened list for chronological order.
Coinbase refuses a single range holding more than 350 candles rather than truncating it, so
keep `start`/`end` within 350 candles of the chosen granularity.

## Coinbase App (v2)

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  page = await client.app.accounts.list(limit=25)          # one page (the whole response frame)
  print(page['data'])

  accounts = await client.app.accounts.list_paged(limit=25)       # every account, flattened
  print(accounts[0]['id'])

  async for page in client.app.accounts.list_paged(limit=25):     # every page, one at a time
    for account in page:
      print(account['id'])

  transactions = await client.app.accounts.transactions.list_paged(account_id='account-id', limit=25)
  print(transactions[0]['id'])
```

## Advanced Trade (v3)

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  page = await client.app.advanced_trade.http.products.list(limit=50)
  print(page['products'])

  products = await client.app.advanced_trade.http.products.list_paged(limit=50)      # every product, flattened
  print(products[0]['product_id'])

  orders = await client.app.advanced_trade.http.orders.historical.batch_paged(order_status=['OPEN'])
  print(len(orders))

  fills = await client.app.advanced_trade.http.orders.historical.fills_paged()
  print(len(fills))
```

## Candles

```python
from datetime import datetime, timedelta, timezone

from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  end = datetime(2026, 9, 4, 8, tzinfo=timezone.utc)
  start = end - timedelta(hours=2)

  candles = await client.app.advanced_trade.http.products.candles_paged(
    'BTC-USD', start=start, end=end, granularity='ONE_MINUTE', limit=60,
  )                                                                   # every candle, newest first
  print(candles[-1]['start'], candles[0]['start'])

  async for page in client.app.advanced_trade.http.products.public.candles_paged(
    'BTC-USD', start=start, end=end, granularity='ONE_MINUTE', limit=60,
  ):                                                                  # one page at a time
    print(page[0]['start'], len(page))
```
