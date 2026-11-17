# Timestamps

Timestamps in requests and responses are timezone-aware `datetime`s in UTC. The client converts to and from the wire format, which varies by field:

| Wire format | Used for |
| --- | --- |
| Unix nanoseconds | the default: trade, order and funding times, candle times and the `from_`/`to` range, history `start_time`/`end_time`, WebSocket `worker_timestamp` |
| Unix seconds | signer `expiration`, allowance `allowance_expiry`, competition start/end times, points epochs, the `oracle` channel's `timestamp`, `cached_at` and maintenance times |
| RFC 3339 strings | affiliate and fee-tier dates |

For these fields you never deal with the units yourself: pass a `datetime` and read a `datetime`.

## Exceptions

- A few fields keep the raw wire value, because their unit is undocumented and can't be read off live data: `markets.all` `display_at`, `boost_starts_at` and `boost_ends_at` have only ever been `"0"`, and `auth.sessions` `created_at`/`last_seen_at`/`expires_at` (integers) and `affiliate.referrals` `last_trade_at` (a string) have never been seen populated.
- Some epoch fields use `0` to mean "none" or "never", which parses to `1970-01-01T00:00:00+00:00`, for example a TP/SL order's `expires_at`/`triggered_at` and `stats.user_trading`'s `last_trade_at`. Treat the epoch as "not set".

## Requests

```python
from datetime import datetime, timedelta, timezone
from typed_risex import RISEx

ACCOUNT = '0xYourAccountAddress'

async with RISEx.new(public=True) as client:
  end = datetime.now(timezone.utc)
  start = end - timedelta(days=7)
  trades = await client.account.trade_history(ACCOUNT, start_time=start, end_time=end)
  candles = await client.markets.candles(market_id=1, from_=end - timedelta(hours=6), to=end)
```

Pass timezone-aware datetimes, as above.

## Responses

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  result = await client.markets.trade_history(market_id=1, limit=1)
  trade = result['trades'][0]
  print(trade['time'].isoformat())
```

## Raw Helpers

To convert a value outside a request, for example a raw frame you stored, `typed_risex.core` exposes the converters:

```python
from datetime import datetime, timezone
from typed_risex.core import timestamp_nanos, timestamp_seconds

when = timestamp_nanos.parse('1763320800000000000')
print(when, timestamp_seconds.dump(datetime(2026, 1, 1, tzinfo=timezone.utc)))
```
