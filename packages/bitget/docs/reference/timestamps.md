# Timestamps

Bitget timestamps are epoch milliseconds. Both request parameters and response fields work
through `datetime` directly — the client converts on the way out and parses on the way in.

## Common Patterns

Pass a `datetime` directly for a window parameter.

```python
from datetime import datetime, timedelta
from typed_bitget import Bitget

async with Bitget.new(public=True) as client:
  candles = await client.classic.mix.candles(
    symbol='BTCUSDT',
    product_type='USDT-FUTURES',
    granularity='1m',
    start_time=datetime.now() - timedelta(hours=1),
    end_time=datetime.now(),
  )
```

Validated response timestamp fields (`ts`, `serverTime`, and similar) come back as `datetime`
objects, not raw integers.

Bitget itself is inconsistent on the wire about how it sends a millisecond timestamp: some
endpoints send it as a JSON number, others (e.g. `serverTime`) send it as a numeric string.
The client normalizes both through the same parser, so this is invisible from the caller's
side — every `TimestampMillis`-typed field parses to `datetime` either way.

## Raw Helpers

Use the helper exported by the client's core when you explicitly need a raw millisecond
integer.

```python
from datetime import datetime
from typed_bitget.core import timestamp_millis as ts

timestamp_ms = ts.dump(datetime.now())
current_ms = ts.now()
parsed = ts.parse(1715200000000)
```
