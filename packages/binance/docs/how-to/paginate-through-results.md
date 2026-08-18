# Paginate Through Results

Endpoints that walk a time range, like candles and aggregate trades, have a `_paged`
counterpart that yields successive windows automatically.

```python
from datetime import datetime, timezone
from binance import Binance

async with Binance.new(public=True) as client:
  async for page in client.spot.market.klines_paged(
    symbol='BTCUSDT',
    interval='1h',
    start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
    end_time=datetime(2026, 1, 2, tzinfo=timezone.utc),
  ):
    for candle in page:
      print(candle)
```

Each page spans `start_time` to `end_time`, and the walk advances that window forward by its
own width until a page comes back empty. A page that comes back full (as many rows as
`limit`) means Binance truncated it — `klines_paged` raises `LogicError` rather than silently
skipping the rows it never saw; pass `allow_truncation=True` to accept the loss and keep
going. Pass `max_pages` to stop after a fixed number of windows regardless.

`client.spot.market.agg_trades_paged` follows the same time-window shape. Many other
`client.spot` products — Simple Earn history, Margin history, and more — also have `_paged`
counterparts, but page by `current`/`size` against a reported `total` instead of walking a
time window, so they take no `allow_truncation` and stop once every page has been fetched.
