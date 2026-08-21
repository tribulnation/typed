# Listen To Your Trades

Use `client.streams` for subscription-style updates.

## Listen To User Fills

`user_fills()` streams fills for a user address. This is the most direct way to listen to your trades.

```python
from typed_hyperliquid import Hyperliquid

user = '0xYourAccountAddress'

async with Hyperliquid.new(public=True) as client:
  async with client.streams.user_fills(user) as fills:
    async for update in fills:
      for fill in update['fills']:
        print(fill['coin'], fill['side'], fill['px'], fill['sz'])
```

If you want partial fills aggregated within the same block, pass `aggregate_by_time=True`.

```python
from typed_hyperliquid import Hyperliquid

user = '0xYourAccountAddress'

async with Hyperliquid.new(public=True) as client:
  async with client.streams.user_fills(user, aggregate_by_time=True) as fills:
    async for update in fills:
      print(update['fills'])
```

## Related User Streams

Depending on the workflow, these may also be useful:

- `order_updates()` for order lifecycle updates
- `open_orders(user, dex)` for the current open-order view
- `user_events()` for a broader feed including fills, funding, and liquidations
- `user_fundings()` and `user_non_funding_ledger_updates()` for account flow streams
