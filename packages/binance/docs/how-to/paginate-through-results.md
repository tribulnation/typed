# Paginate Through Results

Every endpoint Binance pages has a `_paged` counterpart. It returns a `PaginatedResponse`:
iterate it for one page of rows at a time, or `await` it for every row flattened into one
list.

Endpoints that walk a time range, like candles and aggregate trades, move `start_time`
forward: each page that comes back full (as many rows as `limit`, 500 by default for
candles) moves `start_time` to the latest row's timestamp and requests again, never past
`end_time`, until a page comes back short. The boundary row Binance re-serves on the next
page is dropped, so no candle is duplicated or skipped.

```python
from datetime import datetime, timezone
from typed_binance import Binance

async with Binance.new(public=True) as client:
  async for candles in client.spot.http.market.klines_paged(
    symbol='BTCUSDT',
    interval='1h',
    start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
    end_time=datetime(2026, 2, 1, tzinfo=timezone.utc),
  ):
    for candle in candles:
      print(candle)
```

Awaiting the same call gives you the whole month in one list:

```python
from datetime import datetime, timezone
from typed_binance import Binance

async with Binance.new(public=True) as client:
  candles = await client.spot.http.market.klines_paged(
    symbol='BTCUSDT',
    interval='1h',
    start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
    end_time=datetime(2026, 2, 1, tzinfo=timezone.utc),
  )
  print(len(candles))
```

`client.spot.http.market.agg_trades_paged` follows the same shape. Many trades can share
one millisecond, so the rows at the boundary timestamp are matched by content rather than
by timestamp when the next page re-serves them. Both walks raise `LogicError` in the one
case they cannot advance: a full page whose rows all share a single timestamp.

Many other `client.spot.http` products, Simple Earn history, Margin history, and more,
also have `_paged` counterparts. Those page by `current`/`size` against a reported
`total`, or by a cursor Binance hands back, and stop once every page has been fetched.
They are used exactly the same way.

## Checkpoint and resume a long walk

`pages()` yields each page together with the state the following page is fetched with,
and `resume(state)` restarts the walk from a saved one, so a long history walk can be
picked up where it was interrupted.

```python
from datetime import datetime, timezone
from typed_binance import Binance

async with Binance.new(public=True) as client:
  paging = client.spot.http.market.klines_paged(
    symbol='BTCUSDT',
    interval='1m',
    start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
    end_time=datetime(2026, 2, 1, tzinfo=timezone.utc),
  )
  checkpoint = None
  async for page in paging.pages():
    checkpoint = page.next
    if checkpoint is None:
      break

  if checkpoint is not None:
    rest = await paging.resume(checkpoint)
    print(len(rest))
```
