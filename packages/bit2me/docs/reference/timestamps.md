# Timestamps

## Common Patterns

Most Bit2Me response fields (`createdAt`, `updatedAt`, and similar) are ISO 8601 strings on
the wire, and come back to you as plain `datetime` — no manual parsing needed:

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new(public=True) as client:
  orders = await client.v1.trading.orders.list(limit=1)
  if orders:
    print(orders[0].get('createdAt'))  # a `datetime`
```

A smaller set of endpoints — the Trading Spot WebSocket pushes' `nonce`/`timestamp` fields,
and `v2`'s order book and ticker `timestamp` — carry Bit2Me's other wire format,
Unix-epoch-milliseconds, and are typed `typed_bit2me.types.MillisTimestamp`. They validate into a
`datetime` the same way; the difference is invisible once you have the value.

Request-side, `client.v1.trading.candles()`'s time-range parameters take that same
millisecond-epoch shape: pass `datetime` values for `start_time`/`end_time`, and the client
converts them to Bit2Me's millisecond-epoch format for you.

```python
from datetime import datetime, timedelta, timezone
from typed_bit2me import Bit2Me

async with Bit2Me.new(public=True) as client:
  candles = await client.v1.trading.candles(
    symbol='BTC/EUR',
    interval=60,
    start_time=datetime.now(timezone.utc) - timedelta(hours=4),
    end_time=datetime.now(timezone.utc),
    limit=4,
  )
```

`client.v1.trading.orders.list()`, `client.v1.trading.trades.list()`,
`client.v1.currency.ohlca()`, and `client.v1.wallet.transactions.list()` declare
`datetime`-typed range parameters too (`start_time`/`end_time`, `time`, `from_`/`to`), but on
the wire Bit2Me expects an RFC 3339 string there, not a millisecond epoch. The client converts
for you on this shape as well:

```python
from datetime import datetime, timedelta, timezone
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  orders = await client.v1.trading.orders.list(
    start_time=datetime.now(timezone.utc) - timedelta(days=1),
    end_time=datetime.now(timezone.utc),
  )
```

## Raw Helpers

`typed_bit2me.core.timestamp_millis` converts between Bit2Me's millisecond-epoch wire format and
`datetime` directly, for the fields typed `MillisTimestamp`:

```python
from datetime import datetime
from typed_bit2me.core import timestamp_millis as ts

now_ms = ts.now()
dumped_ms = ts.dump(datetime.now())
parsed = ts.parse(1715200000000)
```

`typed_bit2me.core.timestamp_iso` does the same for Bit2Me's RFC 3339 wire format, for the fields
typed `TimestampIso` (`start_time`/`end_time`/`time`/`from_`/`to` on the request side,
`createdAt`/`updatedAt` and similar on responses):

```python
from datetime import datetime
from typed_bit2me.core import timestamp_iso as ts

now_iso = ts.now()
dumped_iso = ts.dump(datetime.now())
parsed = ts.parse('2024-05-07T14:08:30.961Z')
```
