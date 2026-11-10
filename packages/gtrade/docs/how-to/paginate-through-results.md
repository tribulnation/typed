# Paginate Through Results

Four endpoints paginate, each with a single-page method and a `_paged` variant:

| Method | Pages by | Credentials |
| - | - | - |
| `client.trading.account.order_history` | cursor | Agent key or API key |
| `client.trading.account.fills` | cursor | Agent key or API key |
| `client.backend_global.traders.history` | cursor | None |
| `client.backend_global.contests.leaderboard` | offset | None |

All of them return rows newest (or highest-ranked) first.

## One Page At A Time

```python
from typed_gtrade import GTrade

trader = '0x...'

async with GTrade.new() as client:
  page = await client.trading.account.order_history(address=trader, limit=100)
  while True:
    for order in page['data']:
      print(order['id'], order['status'])
    if page['nextCursor'] is None:
      break
    page = await client.trading.account.order_history(address=trader, limit=100, cursor=page['nextCursor'])
```

`limit` goes up to 500 on the Trading API (default 50). `nextCursor` is `None` on the last
page. Backend Global's `traders.history` reports the same under `pagination.nextCursor`.

## Automatic Pagination

A `_paged` method returns a `PaginatedResponse`: await it for every row, or iterate it for
one page of rows at a time.

```python
from typed_gtrade import GTrade

trader = '0x...'

async with GTrade.new() as client:
  fills = await client.trading.account.fills_paged(address=trader, limit=500)  # every row
  print(len(fills))

  async for rows in client.trading.account.order_history_paged(address=trader):
    for order in rows:
      print(order['id'], order['status'])
```

## Filter, Checkpoint and Resume

```python
from datetime import datetime, timezone
from typed_gtrade import GTrade

trader = '0x...'

async with GTrade.new(public=True) as client:
  history = client.backend_global.traders.history_paged(
    address=trader, chain_id=42161, pair='BTC/USD',
    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
  )
  async for page in history.pages():
    print(len(page.rows), page.next)  # save page.next to resume later
    if page.next is not None:
      rest = await history.resume(page.next)  # every row after this page
      break
```

`pages()` exposes each page's state: `page.next` is what the following page is fetched
with, `None` after the last one. `resume(state)` continues a walk from a saved state, and
retrying a failed page is safe because every page fetch only reads.

`traders.batch_history` reads several traders at once and pages each one through its own
cursor in `cursors`; it has no `_paged` variant.
