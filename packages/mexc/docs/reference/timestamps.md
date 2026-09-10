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
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  await client.spot.http.market.candles(
    symbol='BTCUSDT',
    interval='1m',
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now(),
  )
  await client.futures.http.market.candles(
    'BTC_USDT',
    interval='Min1',
    start=datetime.now() - timedelta(hours=1),
    end=datetime.now(),
  )
```

Timestamp parameters take `datetime` only. If you already have a raw venue-formatted
integer, convert it first with `ts.parse` (see Raw Helpers below).

```python
from typed_mexc import MEXC
from typed_mexc.core import timestamp_millis as ts, timestamp_seconds as ts_s

async with MEXC.new(public=True) as client:
  await client.spot.http.market.candles(
    symbol='BTCUSDT',
    interval='1m',
    start_time=ts.parse(1715200000000),
  )
  await client.futures.http.market.candles(
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
from typed_mexc.core import timestamp_millis as ts

timestamp_ms = ts.dump(datetime.now())
current_ms = ts.now()
parsed = ts.parse(1715200000000)
```

For second-based values, use `timestamp_seconds`.

```python
from datetime import datetime
from typed_mexc.core import timestamp_seconds as ts_s

timestamp_secs = ts_s.dump(datetime.now())
```
