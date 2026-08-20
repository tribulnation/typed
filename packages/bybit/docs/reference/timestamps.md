# Timestamps

Bybit's wire format is millisecond (mostly) or second epochs, but Typed Bybit does not make
you handle raw integers. Every timestamp parameter and response field is a real `datetime` —
`TimestampMillis`, `TimestampSeconds`, or `TimestampIso`, each `Annotated[datetime, ...]` —
converted at the boundary. Pass a `datetime` in, get a `datetime` back.

## Request Parameters

Bound a range with real `datetime` values, not integers:

```python
from datetime import datetime, timedelta, timezone
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  end = datetime.now(timezone.utc)
  start = end - timedelta(hours=24)
  candles = await client.http.market.kline(
    category='spot', symbol='BTCUSDT', interval='60', start=start, end=end,
  )
  print(len(candles['list']))
```

`start`/`end` on `market.kline` and `start_time`/`end_time` on `market.funding_history` are
typed `TimestampMillis | None`; the client serializes them to Bybit's millisecond epoch on
the wire. A naive `datetime` (no `tzinfo`) is treated as UTC.

## Response Fields

A response field declared as a timestamp — `market.funding_history`'s
`fundingRateTimestamp`, `trade.order_history`'s `createdTime`/`updatedTime`, and the rest —
comes back as a `datetime` already, no manual parsing needed:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  history = await client.http.market.funding_history(category='linear', symbol='BTCUSDT')
  print(history['list'][0]['fundingRateTimestamp'].isoformat())
```

Not every timestamp-shaped value gets this treatment. Positional row series — `market.kline`
and its siblings — return each candle as a plain tuple of strings, so the leading start-time
column stays a `str` millisecond epoch. Convert it explicitly if you need a `datetime`:

```python
from datetime import datetime, timezone
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  candles = await client.http.market.kline(category='spot', symbol='BTCUSDT', interval='60')
  start_ms = int(candles['list'][0][0])
  print(datetime.fromtimestamp(start_ms / 1000, tz=timezone.utc))
```

## Units Vary By Field

Most of the client uses `TimestampMillis`. A handful of fields use `TimestampSeconds`
instead — check the parameter's or field's own type in the generated source
(`Annotated[datetime, ...]`'s underlying converter) rather than assuming millis everywhere;
the docstring names the wire unit either way. Both render as the same `datetime` type, so
code that only reads the value never needs to know which one it was.
