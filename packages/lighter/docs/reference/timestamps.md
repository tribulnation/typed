# Timestamps

Lighter mixes timestamp units on the wire:

- **Epoch milliseconds**: most REST and WebSocket times: trades, candles, range bounds
  such as `start_timestamp`/`end_timestamp`, order and transaction expiries, transfers,
  RFQs.
- **Epoch microseconds**: `transaction_time` (orders, trades, transactions, accounts, API
  keys, liquidations; REST and WebSocket) and the order book and ticker streams'
  `last_updated_at`.
- **Epoch seconds**: an order's `timestamp`, `created_at` and `updated_at`; account, pool
  and announcement `created_at`; funding and PnL points; auth-token expiries; the status
  endpoint's `timestamp`.
- **RFC 3339 strings**: explorer times (block and batch `updated_at`, log `time`) and
  notification `created_at`/`updated_at`.

The client hides all of it: every one of those fields is a timezone-aware UTC `datetime`,
in both directions.

## Requests

Pass `datetime` objects. Use timezone-aware values: in a read request a naive `datetime`
is read as local time, and anything that gets signed (transaction and order expiries,
`cancel_all_orders`' `cancel_at`, integrator approval expiries, auth-token expiries, the
signer's `expires_at`) refuses a naive `datetime` with `BadRequest`, since a signed time in
the wrong zone would be silently hours off.

```python
from datetime import datetime, timedelta, timezone

from typed_lighter import Lighter

async with Lighter.new() as client:
  end = datetime.now(timezone.utc)
  candles = await client.api.markets.candles(
    market_id=0, resolution='1h', start_timestamp=end - timedelta(hours=6), end_timestamp=end, count_back=6
  )

  await client.tx.create_order({
    'order_type': 'limit',
    'market_index': 0,
    'client_order_index': 1,
    'base_amount': 500,
    'is_ask': False,
    'price': 200_000,
    'time_in_force': 'good-till-time',
    'order_expiry': end + timedelta(days=1),
  })
```

## Responses

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  trades = await client.api.markets.recent_trades(market_id=0, limit=1)
  for trade in trades['trades'] or []:  # `null` when the market has no trades
    print(trade['timestamp'].isoformat())  # datetime, UTC
```

Calendar-only values (the historical trades export's `date`) are `date` objects.

Where Lighter sends `0` for "not set" (an account's `cancel_all_time` with no cancel-all
scheduled, an immediate-or-cancel order's expiry), the field parses to the Unix epoch,
`datetime(1970, 1, 1, tzinfo=timezone.utc)`.

## Exceptions

A few fields stay plain numbers or strings because Lighter's own format for them is not a
single timestamp:

- `api.account.orders.inactive`'s `between_timestamps` filter is a string,
  `"<start>-<end>"` in epoch seconds.
- `api.account.orders.trades`' `from_` is a position in the chosen `sort_by` order, which
  is a timestamp only when sorting by `timestamp`.
- Some integer fields named like times (`trigger_time`, `expire_at`) are returned as
  Lighter sends them.

## Raw Helpers

The converters behind the typed fields are exported from `typed_lighter.core`, one per
wire format, for data you fetch or store yourself:

```python
from datetime import datetime, timezone

from typed_lighter.core import timestamp_millis, timestamp_seconds

now = datetime.now(timezone.utc)
millis = timestamp_millis.dump(now)            # int, epoch milliseconds
back = timestamp_millis.parse(1790240052712)   # datetime, UTC
seconds = timestamp_seconds.dump(now)
```

`timestamp_micros`, `timestamp_iso` and `date_iso` work the same way.
