# Listen To Live Streams

`client.streams` subscribes over Nado's subscriptions WebSocket. Every stream on a client
shares one connection, opened on the first subscription. Each event is validated and typed;
prices and sizes are x18 integers, `timestamp`s are `datetime`s.

## Public Streams

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  async with client.streams.trade(2) as trades:  # BTC-PERP
    async for trade in trades:
      side = 'buy' if trade['is_taker_buyer'] else 'sell'
      print(trade['timestamp'], side, trade['price'] / 10**18, trade['taker_qty'] / 10**18)
```

Leaving the `async with` block unsubscribes. The other public streams:

| Method | Events |
| --- | --- |
| `best_bid_offer(product_id)` | top of book on every change |
| `all_bbo()` | top of book of every product |
| `book_depth(product_id)` | incremental order-book updates (`bids`/`asks` as `(price_x18, size_x18)`) |
| `latest_candlestick(product_id, granularity=...)` | the forming candle |
| `funding_rate(product_id=None)` | funding updates; omit the product for all of them |
| `liquidation(product_id=None)` | liquidations |

## Your Fills, Positions And Orders

`fill`, `position_change` and `order_update` default to your own subaccount on a signing
client. `order_update` requires a key: the client authenticates the connection for you.

```python
from typed_nado import Nado

async with Nado.new() as client:
  async with client.streams.order_update(product_id=2) as updates:
    async for update in updates:
      print(update['digest'], update['reason'], update.get('id'))
```

`order_update` events carry no subaccount, so the client cannot tell apart two
`order_update` subscriptions for different subaccounts: every `order_update` subscription
on one client receives the events of all of them (still filtered by `product_id` when it
names one). Follow one subaccount's orders per client, or match `digest` against the orders
you placed.

`fill` and `position_change` are public: pass any subaccount (`bytes32` hex) as the first
argument to follow it, with or without a key.

```python
from typed_nado import Nado
from typed_nado.core import subaccount_bytes32

me = subaccount_bytes32('0xYourWalletAddress', 'default')

async with Nado.new(public=True) as client:
  async with client.streams.fill(me) as fills:
    async for fill in fills:
      print(fill['order_digest'], fill['filled_qty'] / 10**18, fill['price'] / 10**18)
```

## Without A Context Manager

Await the stream instead to keep it open beyond one block, and unsubscribe yourself:

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  bbo = await client.streams.best_bid_offer(2)
  async for event in bbo:
    print(event['bid_price'] / 10**18, event['ask_price'] / 10**18)
    break
  await bbo.unsubscribe()
```
