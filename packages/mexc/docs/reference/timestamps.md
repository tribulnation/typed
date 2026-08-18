# Timestamps

MEXC accepts `datetime` objects for timestamp parameters. The client converts them to the integer format MEXC expects for each endpoint.

## Common Patterns

Pass a `datetime` directly when filtering a time window.

```python
from datetime import datetime, timedelta

end_time = datetime.now()
start_time = end_time - timedelta(hours=1)
```

This works for spot endpoints that use milliseconds and futures K-line endpoints that use seconds.

```python
from datetime import datetime, timedelta
from mexc import MEXC

async with MEXC.public() as client:
  await client.spot.market.candles(
    symbol='BTCUSDT',
    interval='1m',
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now(),
  )
  await client.futures.market.candles(
    'BTC_USDT',
    interval='Min1',
    start=datetime.now() - timedelta(hours=1),
    end=datetime.now(),
  )
```

Timestamp parameters take `datetime` only. If you already have a raw venue-formatted
integer, convert it first with `ts.parse` (see Raw Helpers below).

```python
from mexc import MEXC
from mexc.core import timestamp as ts, timestamp_s as ts_s

async with MEXC.public() as client:
  await client.spot.market.candles(
    symbol='BTCUSDT',
    interval='1m',
    start_time=ts.parse(1715200000000),
  )
  await client.futures.market.candles(
    'BTC_USDT',
    interval='Min1',
    start=ts_s.parse(1715200000),
  )
```

Validated response timestamp fields are returned as `datetime` objects.

## Raw Helpers

Use the helper exported by the client when you explicitly need raw millisecond integers.

```python
from datetime import datetime
from mexc.core import timestamp as ts

timestamp_ms = ts.dump(datetime.now())
current_ms = ts.now()
parsed = ts.parse(1715200000000)
```

For second-based values, use `timestamp_s`.

```python
from datetime import datetime
from mexc.core import timestamp_s as ts_s

timestamp_s = ts_s.dump(datetime.now())
```
