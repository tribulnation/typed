# Paginate Through Results

Many history and market-data methods have a `_paged` variant that walks every page for you:
candles, aggregate and historical trades, funding rates, orders, fills, income, margin
history and spot transaction history, plus the paged builder and announcement endpoints.

## One Page At A Time

The plain method makes one request and returns one page:

```python
from datetime import datetime, timezone

from typed_aster import Aster

async with Aster.new(public=True) as client:
  candles = await client.futures.market.klines(
    'BTCUSDT',
    interval='1m',
    start_time=datetime(2026, 9, 1, tzinfo=timezone.utc),
    limit=500,
  )
  print(len(candles))
```

## Automatic Pagination

The `_paged` method takes the same arguments. Await it for every row, or iterate it for one
page at a time:

```python
from datetime import datetime, timezone

from typed_aster import Aster

async with Aster.new(public=True) as client:
  walk = client.futures.market.klines_paged(
    'BTCUSDT',
    interval='1m',
    start_time=datetime(2026, 9, 1, tzinfo=timezone.utc),
    end_time=datetime(2026, 9, 2, tzinfo=timezone.utc),
  )
  candles = await walk  # every candle in the range

  async for page in walk:  # or one page at a time
    print(len(page), page[0][0])
```

Walks by time or id move from oldest to newest, except
`client.futures.trade.force_orders_paged`, which moves newest to oldest.

## Account History

The same pattern works for signed history:

```python
from datetime import datetime, timedelta, timezone

from typed_aster import Aster

async with Aster.new() as client:
  since = datetime.now(timezone.utc) - timedelta(days=1)
  fills = await client.futures.trade.user_trades_paged('BTCUSDT', start_time=since)
  orders = await client.spot.trade.all_orders_paged('ASTERUSDT', start_time=since)
  income = await client.futures.account.income_paged(income_type='REALIZED_PNL')
  print(len(fills), len(orders), len(income))
```

Fill and order walks (`user_trades_paged`, `all_orders_paged`) start either from an id
(`from_id`, `order_id`) or from `start_time`, optionally with `end_time`. Aster refuses an
id together with a time filter, so the time filters go out with the first request only;
later pages continue by id, and rows after `end_time` are dropped. Passing both, or
neither, raises `ValueError`.

## Retry And Resume

Each page is fetched from a saved state, so a failed page can be retried and a walk resumed:

```python
from datetime import datetime, timedelta, timezone

from typed_aster import Aster

async with Aster.new() as client:
  since = datetime.now(timezone.utc) - timedelta(days=1)
  walk = client.futures.trade.all_orders_paged('BTCUSDT', start_time=since)
  async for page in walk.pages():
    print(len(page.rows))
    checkpoint = page.next  # pass to walk.resume(checkpoint) to continue later
```
