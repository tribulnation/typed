# Timestamps

Binance timestamps are millisecond epoch integers, UTC — uniform across every surface (spot,
USD-M futures, COIN-M futures, options, portfolio margin, and their streams/WS-API
counterparts). `datetime` works natively as a request parameter end-to-end: pass a `datetime`
directly, and the client converts it to the millisecond integer Binance expects.

## Common Patterns

Pass a `datetime` directly when filtering a time window.

```python
from datetime import datetime, timedelta
from binance import Binance

async with Binance.new(public=True) as client:
  candles = await client.spot.market.klines(
    symbol='BTCUSDT',
    interval='1m',
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now(),
  )
```

Validated response timestamp fields — like `E`/`T` on stream events, `SpotTrade.time`, or the
open/close-time entries of a `SpotCandle` row — come back as `datetime` objects too. A
handful of order-book-depth response fields (e.g. `usdm_futures.market.depth`'s `E`/`T`) are
typed as raw millisecond `int` instead, not `Timestamp` — convert those manually with
`timestamp.parse()` if you need a `datetime`.

## Raw Helpers

Use the helper exported by the client when you already have a raw millisecond integer, or
need one.

```python
from datetime import datetime
from binance.core import timestamp

timestamp_ms = timestamp.dump(datetime.now())
current_ms = timestamp.now()
parsed = timestamp.parse(1715200000000)
```
