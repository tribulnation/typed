# Timestamps

## Common Patterns

Most validated response timestamp fields come back as a `datetime` (UTC) — the client
decodes KuCoin's millisecond epoch integers automatically, via the shared `Timestamp`
type used across Spot, Margin, Futures, Earn and streaming responses. You don't parse
these yourself.

```python
from kucoin import KuCoin

async with KuCoin.new() as client:
  orders = await client.spot.stop_orders.get_list()
  for order in orders['items']:
    print(order['createdAt'])  # a datetime
```

A few response fields are the exception and stay a plain millisecond `int` instead of
`datetime` — for example `account.ledgers`'s `createdAt`. Check the field's own type in
the generated response before assuming it's a `datetime`.

Request-side timestamp parameters are **not** uniform across the client — check the
parameter's docstring for the specific method you're calling:

- Order-history endpoints (`spot.orders_hf.get_trade_history`,
  `spot.orders_hf.get_closed_orders`, `spot.oco_orders.get_list`,
  `spot.stop_orders.get_list`, and their `margin.*` equivalents) accept a `datetime`
  directly for `start_at`/`end_at` — the client converts it to KuCoin's millisecond epoch
  integer for you.

  ```python
  from datetime import datetime, timedelta
  from kucoin import KuCoin

  async with KuCoin.new() as client:
    trades = await client.spot.orders_hf.get_trade_history(
      symbol='BTC-USDT',
      start_at=datetime.now() - timedelta(days=1),
      end_at=datetime.now(),
    )
  ```

- Other endpoints take a plain `int` instead, and the unit is **not** consistent between
  them. Most (for example `futures.funding_fees.private_funding_history`'s `start_at`/
  `end_at`, `affiliate.trade_history`'s `trade_start_at`/`trade_end_at`) are Unix
  **milliseconds**, matching every response field. `spot.klines`'s `start_at`/`end_at` are
  the one confirmed exception: Unix **seconds**, not milliseconds, despite sitting right
  next to millisecond-based endpoints elsewhere in the client. Always read the parameter's
  docstring rather than assuming a unit.

  ```python
  from kucoin import KuCoin

  async with KuCoin.new(public=True) as client:
    candles = await client.spot.klines(     # start_at/end_at are Unix SECONDS here
      symbol='BTC-USDT', type='1hour',
      start_at=1_700_000_000, end_at=1_700_100_000,
    )
    history = await client.futures.funding_fees.private_funding_history(  # ms here
      symbol='XBTUSDTM', start_at=1_700_000_000_000, end_at=1_700_100_000_000,
    )
  ```

## Raw Helpers

Use `kucoin.core.timestamp` when you need to convert a `datetime` to/from KuCoin's
millisecond epoch integer by hand — for example, to build the raw `int` a
non-`datetime` endpoint expects.

```python
from datetime import datetime
from kucoin.core import timestamp

timestamp_ms = timestamp.dump(datetime.now())
current_ms = timestamp.now()
parsed = timestamp.parse(1715200000000)
```

There is no equivalent helper for `spot.klines`'s second-based `start_at`/`end_at` —
convert manually, for example `int(dt.timestamp())`.
