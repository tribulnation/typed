# Timestamps

Bybit speaks millisecond epochs. Request parameters that bound a range — `start`/`end` on
`market.kline`, `start_time`/`end_time` on `market.funding_history`, and the rest — take a raw
`int` millisecond timestamp. No request parameter accepts a `datetime` directly; convert with
the helper below.

Response fields are left exactly as Bybit sends them — sometimes an `int`, sometimes a `str`
of the same epoch — so a response value should be converted explicitly at the call site too.

## Common Patterns

```python
from bybit import Bybit, timestamp

async with Bybit.new(public=True) as client:
  end = timestamp.now()               # int, current time in milliseconds
  start = end - 24 * 60 * 60 * 1000    # 24 hours earlier
  candles = await client.http.market.kline(
    category='spot', symbol='BTCUSDT', interval='60', start=start, end=end,
  )
  print(timestamp.parse(candles['list'][0][0]))  # -> datetime
```

`timestamp.parse` accepts an `int`, a `str`, or an already-parsed `datetime`; `timestamp.dump`
converts a `datetime` (or an already-raw epoch) back into the `int` a request parameter takes.

## Raw Helpers

```python
from datetime import datetime
from bybit import timestamp

timestamp.now()                    # -> int, current millisecond epoch
timestamp.parse('1785337186448')   # -> datetime
timestamp.dump(datetime.now())     # -> int
```

`bybit.timestamp` exists for manual conversion — nothing in the client wires a `datetime`
object into a request parameter for you.
