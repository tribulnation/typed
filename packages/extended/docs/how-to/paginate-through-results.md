# Paginate Through Results

History endpoints are cursor-paginated. Each has a `_paged` variant that follows the cursor
for you:

- `client.account.trades_paged(...)`
- `client.account.orders_history_paged(...)`
- `client.account.positions_history_paged(...)`
- `client.account.funding_history_paged(...)`
- `client.account.asset_operations_paged(...)` (deposits, withdrawals, transfers)
- `client.portfolio.funding_history_paged(...)`
- `client.builder.trades_paged(...)`

They take the same filters as the single-page call, minus `cursor`, and return rows newest
first. `limit` sets the page size.

## Every Row At Once

Awaiting a paged call fetches every page and returns one flat list:

```python
from typed_extended import Extended

async with Extended.new() as client:
  trades = await client.account.trades_paged(['BTC-USD'], limit=100)
  print(len(trades), trades[0]['createdTime'] if trades else None)
```

## One Page At A Time

Iterate to process pages as they arrive, and stop early whenever you have enough:

```python
from datetime import datetime, timezone
from typed_extended import Extended

cutoff = datetime(2026, 1, 1, tzinfo=timezone.utc)

async with Extended.new() as client:
  async for page in client.account.trades_paged(['BTC-USD'], limit=100):
    for trade in page:
      print(trade['createdTime'], trade['side'], trade['price'], trade['qty'])
    if page[-1]['createdTime'] < cutoff:
      break
```

## Resuming A Walk

`pages()` exposes each page's cursor, so a long walk can be checkpointed and resumed later:

```python
from typed_extended import Extended

async with Extended.new() as client:
  walk = client.account.orders_history_paged(market=['BTC-USD'], limit=100)
  cursor = None
  async for page in walk.pages():
    print(len(page.rows))
    cursor = page.next
    break
  if cursor is not None:
    rest = await walk.resume(cursor)
```

Several history endpoints return at most 10,000 records in total, however many pages you
fetch.

## Market Data History

Candles and funding rates have `_paged` variants too. They walk back in time, newest first,
by moving `end_time` to the oldest row of each page:

- `client.info.candles_paged(...)`: from `end_time` (or now) back to the market's first
  candle, unless you stop earlier. For monthly (`P30D`) candles, pass `limit` of at least 2.
- `client.info.funding_rates_paged(...)`: everything between `start_time` and `end_time`,
  however many 1000-rate pages that takes.

```python
from datetime import datetime, timezone
from typed_extended import Extended

since = datetime(2026, 1, 1, tzinfo=timezone.utc)
until = datetime(2026, 7, 1, tzinfo=timezone.utc)

async with Extended.new(public=True) as client:
  funding = await client.info.funding_rates_paged(
    'BTC-USD', start_time=since, end_time=until
  )
  async for page in client.info.candles_paged(
    'BTC-USD', candle_type='trades', interval='PT1H', limit=2800, end_time=until
  ):
    print(len(page), page[-1]['T'])
    if page[-1]['T'] < since:
      break
```
