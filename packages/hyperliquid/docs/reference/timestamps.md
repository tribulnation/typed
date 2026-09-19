# Timestamps

Pass Python `datetime` values to parameters annotated as `TimestampMillis`, including
`start_time` and `end_time`. Use timezone-aware values to make the intended time zone
explicit. The client serializes them into Hyperliquid's integer milliseconds automatically.
With response validation enabled, timestamp fields are converted back to `datetime`.

## Time Windows

```python
from datetime import datetime, timedelta, timezone

end_time = datetime.now(timezone.utc)
start_time = end_time - timedelta(hours=1)
```

Pass these values directly to methods such as `info.user_fills_by_time()` or
`info.user_non_funding_ledger_updates_paged()`.

## Existing Millisecond Timestamps

Convert an integer timestamp into a `datetime` before passing it to the client:

```python
from typed_hyperliquid.core import timestamp_millis as ts

start_time = ts.parse(1789504834597)
```

`ts.now()` and `ts.dump(value)` return integer milliseconds for working with raw wire
data. Parameters annotated as `TimestampMillis` expect a `datetime`, so use
`datetime.now(timezone.utc)` or `ts.parse(milliseconds)` for those inputs.
