# Listen To Live Streams

`client.streams` subscribes to EVEDEX's WebSocket (Centrifugo) channels over one shared
connection, opened on the first subscription. Every publication is a full snapshot, not a
delta: keep the newest one per entity, by `updatedAt`, `createdAt` or `t`.

Each stream method returns a subscription you can use with `async with` (unsubscribes on
exit) or `await` (unsubscribe yourself); see [Async Usage](../reference/async-usage.md).

## Public Channels

Public channels need no credentials.

```python
from typed_evedex import Evedex

async with Evedex.new(public=True) as client:
  async with client.streams.order_book_best('BTCUSD') as stream:
    async for update in stream:
      book = update['orderBook']
      print(book['t'], book['bids'][0]['price'], book['asks'][0]['price'])
      break
```

| Method | Publishes |
| --- | --- |
| `order_book(instrument, round=...)` | Full order book, prices grouped by `round` |
| `order_book_best(instrument)` | Best bid and ask |
| `recent_trades(instrument)` / `trades(instrument)` | Public trades, one per publication |
| `candles(instrument, group=...)` | The candle currently forming, same tuple as the REST history |
| `instruments()` | Every instrument with prices and metrics |
| `funding_rates()` | Funding-rate updates, one instrument per publication |
| `coin_prices()` | Index price of every coin |
| `info()` | Matching-engine state; anything other than `active` halts trading |
| `heartbeat()` | Server time about every second |

```python
from typed_evedex import Evedex

async with Evedex.new(public=True) as client:
  async with client.streams.candles('BTCUSD', group='1m') as stream:
    async for open_time, open_, close, high, low, volume_usd, volume in stream:
      print(open_time, close)
      break
```

## Private Channels

Account channels live under `client.streams.account` and need the wallet private key: the
client signs in and authorizes each subscription with its session. An API key cannot open
them.

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  async with client.streams.account.orders() as stream:
    async for order in stream:
      print(order['id'], order['status'], order['unFilledQuantity'])
```

| Method | Publishes |
| --- | --- |
| `orders()` | Order snapshots on every status or fill change |
| `fills()` | Your executions, one per publication |
| `fees()` | Fees charged on your fills |
| `positions()` | Position snapshots, including leverage changes |
| `tpsl()` | Take-profit/stop-loss snapshots |
| `funding()` | Trading-balance snapshots, one coin per publication |
| `transfers()` | Deposit, withdrawal and balance-move snapshots |
| `user()` | Account state; `marginCall` true means reduce risk now |

A common pattern is to subscribe first, then fetch the REST snapshot (for example
`client.exchange.orders.opened()`) and keep whichever copy of each entity is newer.

## Several Streams at Once

```python
import asyncio
from typed_evedex import Evedex

async with Evedex.new() as client:
  async def watch_fills():
    async with client.streams.account.fills() as stream:
      async for fill in stream:
        print('fill', fill)

  async def watch_positions():
    async with client.streams.account.positions() as stream:
      async for position in stream:
        print('position', position)

  await asyncio.gather(watch_fills(), watch_positions())
```

If the heartbeat goes silent for more than 30 seconds, treat the connection as lost. A
dropped connection ends its streams with `NetworkError`; reconnect and resubscribe.
