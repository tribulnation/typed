# Timestamps

## Common Patterns

Most validated response timestamp fields come back as a `datetime` (UTC) — the client
decodes KuCoin's epoch integers automatically, via the shared `TimestampMillis` (or, for a
handful of endpoints, `TimestampSeconds`) type used across Spot, Margin, Futures, Earn and
streaming responses. You don't parse these yourself.

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  orders = await client.spot.stop_orders.get_list()
  for order in orders['items']:
    print(order['createdAt'])  # a datetime
```

A few response fields are the exception and stay a plain millisecond `int` instead of
`datetime` — for example `account.ledgers`'s `createdAt`. Check the field's own type in
the generated response before assuming it's a `datetime`.

Every `start_at`/`end_at`-shaped request parameter across the client (order-history
endpoints like `spot.orders_hf.get_trade_history`, `spot.orders_hf.get_closed_orders`,
`spot.oco_orders.get_list`, `spot.stop_orders.get_list` and their `margin.*` equivalents,
account/broker/convert history endpoints, and `futures`/`affiliate` windows) accepts a real
`datetime` directly — the client converts it to KuCoin's own epoch integer for you, so you
never build the raw integer by hand:

```python
from datetime import datetime, timedelta
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  trades = await client.spot.orders_hf.get_trade_history(
    symbol='BTC-USDT',
    start_at=datetime.now() - timedelta(days=1),
    end_at=datetime.now(),
  )
```

The one thing that's **not** uniform is the wire unit the client converts your `datetime`
into. Most endpoints (for example `futures.funding_fees.private_funding_history`'s
`start_at`/`end_at`, `affiliate.trade_history`'s `trade_start_at`/`trade_end_at`) encode
Unix **milliseconds**, matching every response field. `spot.klines`'s `start_at`/`end_at`
are the one exception: Unix **seconds**, not milliseconds. This is purely an internal
conversion detail; you always pass a `datetime` either way.

```python
from datetime import datetime, timedelta
from typed_kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  candles = await client.spot.klines(     # start_at/end_at encode Unix SECONDS on the wire
    symbol='BTC-USDT', type='1hour',
    start_at=datetime.now() - timedelta(hours=1), end_at=datetime.now(),
  )
  history = await client.futures.funding_fees.private_funding_history(  # ms on the wire
    symbol='XBTUSDTM',
    start_at=datetime.now() - timedelta(hours=1), end_at=datetime.now(),
  )
```

## Raw Helpers

Use `typed_kucoin.core.timestamp_millis` (or `timestamp_seconds`, for `spot.klines`'s
second-based `start_at`/`end_at`) when you need to convert a `datetime` to/from KuCoin's
epoch integer by hand.

```python
from datetime import datetime
from typed_kucoin.core import timestamp_millis

timestamp_ms = timestamp_millis.dump(datetime.now())
current_ms = timestamp_millis.now()
parsed = timestamp_millis.parse(1715200000000)
```
