# Timestamps

## Common Patterns

Most Bit2Me response fields (`createdAt`, `updatedAt`, and similar) are ISO 8601 strings on
the wire, and come back to you as plain `datetime` — no manual parsing needed:

```python
from bit2me import Bit2Me

async with Bit2Me.public() as client:
  orders = await client.v1.trading.orders.list(limit=1)
  if orders:
    print(orders[0].get('createdAt'))  # a `datetime`
```

A smaller set of endpoints — the Trading Spot WebSocket pushes' `nonce`/`timestamp` fields,
and `v2`'s order book and ticker `timestamp` — carry Bit2Me's other wire format,
Unix-epoch-milliseconds, and are typed `bit2me.types.MillisTimestamp`. They validate into a
`datetime` the same way; the difference is invisible once you have the value.

Request-side, `client.v1.trading.candles()` is the one endpoint whose time-range parameters
are fully wired: pass `datetime` values for `start_time`/`end_time`, and the client converts
them to Bit2Me's millisecond-epoch format for you.

```python
from datetime import datetime, timedelta, timezone
from bit2me import Bit2Me

async with Bit2Me.public() as client:
  candles = await client.v1.trading.candles(
    symbol='BTC/EUR',
    interval=60,
    start_time=datetime.now(timezone.utc) - timedelta(hours=4),
    end_time=datetime.now(timezone.utc),
    limit=4,
  )
```

**Not every date-range parameter is wired this way.** `client.v1.trading.orders.list()`,
`client.v1.trading.trades.list()`, and `client.v1.currency.ohlca()` all also declare
`datetime`-typed range parameters (`start_time`/`end_time`, `time`), but pass the value
straight into the query string without converting it first — unlike `candles()`. Against
`orders.list()`, this reliably fails with an HTTP 400 (`INVALID_FORMAT`,
`"Object didn't pass validation for format date-time"`): Bit2Me expects a proper ISO 8601
string there, and Python's default `datetime` string representation isn't one. Until this is
fixed client-side, avoid `start_time`/`end_time`/`time` on these three calls and filter
results client-side instead, or fetch without a date range.

## Raw Helpers

`bit2me.core.timestamp` converts between Bit2Me's millisecond-epoch wire format and
`datetime` directly, for the fields typed `MillisTimestamp`:

```python
from datetime import datetime
from bit2me.core import timestamp as ts

now_ms = ts.now()
dumped_ms = ts.dump(datetime.now())
parsed = ts.parse(1715200000000)
```
