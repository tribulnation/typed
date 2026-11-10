# Listen To Live Streams

Three WebSocket feeds, each opened on its first subscription:

| Feed | Methods | Credentials |
| - | - | - |
| Trading API channels | `client.trading.streams.*` | Public channels: none. Private channels: agent key or API key |
| Backend contract events | `client.backend.streams.*` | None |
| Live prices | `client.pricing.streams.*` | None |

A subscription is an async iterator. Leaving the `async with` block unsubscribes; see
[Async Usage](../reference/async-usage.md) for the `await` + `unsubscribe()` style. If the
connection drops, the iterator raises `NetworkError`; see [Reconnect](#reconnect).

A client holds one subscription per channel and keys (`book('BTC-USD')` and
`book('BTC/USD')` are the same): subscribing again while it is open raises `RuntimeError`
(`Already subscribed to channel ...`), so two consumers should share one subscription.

## Trading API: Public Channels

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  async with client.trading.streams.book('BTC/USD') as books:
    async for frame in books:
      book = frame['data']
      print(frame['seq'], book['markPrice'], book['bids'][0]['price'], book['asks'][0]['price'])
```

Every frame carries `snapshot`: the first frame after subscribing is a full snapshot, the
rest are updates. On `prices` and `book`, `seq` increases by one per frame; a gap means a
missed frame, so resubscribe for a fresh snapshot.

| Method | Snapshot | Updates |
| - | - | - |
| `prices()` | every market's mark and index price | batches of changed prices |
| `book(market)` | the full virtual book | the full book on change |
| `trades(market)` | the latest trades | new trades |
| `candles(market, interval=...)` | the latest candles | the live candle |

## Trading API: Private Channels

```python
from typed_gtrade import GTrade

async with GTrade.new() as client:
  async with client.trading.streams.orders() as frames:
    async for frame in frames:
      if frame['snapshot'] is True:
        print('open orders:', [order['id'] for order in frame['data']])
      else:
        order = frame['data']
        print(order['id'], order['status'], order['reason'])
```

Check `frame['snapshot'] is True` (not just `if frame['snapshot']`) so your type checker
knows a snapshot's `data` is a list and an update's a single order.

The connection authenticates itself before the first private subscription, with the API key
when the client has one, else the agent signature. Private channels are scoped to the
credential's trader:

| Method | Snapshot | Updates |
| - | - | - |
| `orders()` | open orders (a list) | one order per status change |
| `fills()` | empty | the order that filled |
| `positions()` | open positions with live PnL | the full list on change |
| `account()` | balances, fee tier, agents | the account, periodically |

## Backend Contract Events

The per-chain backend pushes the Diamond's events to every connection; there is nothing to
subscribe to on the wire. Each method yields one event type:

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  async with client.backend.streams.register_trade() as trades:
    async for container in trades:
      trade = container['trade']
      print(trade['user'], trade['pairIndex'], trade['long'], trade['openPrice'])
```

Values are raw contract-precision integers, as on `client.backend`, except
`new_trade_history()`, which pushes normalized numbers (see
[Numbers & Precision](../reference/numbers.md)). Useful events:

- `current_block()`: the chain's latest block number.
- `register_trade()`, `update_trade()`, `unregister_trade()`: open trades and orders as the
  backend registers, changes and removes them.
- `live_event()`: raw confirmed Diamond events (`event`, `transactionHash`, `blockNumber`,
  `returnValues`); `unconfirmed_event()` pushes them before confirmation.
- `trading_variables()`: the whole trading-variables payload, about 3 MB, about once a minute.

### Latest-Value Feeds

`current_block()`, `current_gas()`, `current_l1_block()`, `trading_variables()` and
pricing's `heartbeat()` keep only the newest frame: a consumer slower than the feed jumps
to the latest one instead of building a backlog, so you can miss values (block numbers, for
example). The subscription's `skipped` counts the frames dropped so far. Every other feed
and channel delivers every frame, in order.

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  async with client.backend.streams.current_block() as blocks:
    async for block in blocks:
      print(block, blocks.skipped)
```

## Live Prices

The pricing feed pushes flat `[pairIndex, price, pairIndex, price, ...]` arrays of the pairs
whose price changed, with float prices:

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  async with client.pricing.streams.prices() as batches:
    async for batch in batches:
      for pair_index, price in zip(batch[::2], batch[1::2]):
        print(int(pair_index), price)
```

Map a `pairIndex` to its symbol with `client.trading.markets.list()`. `heartbeat()` yields
the server time about once a second, as a one-element tuple ([latest value
only](#latest-value-feeds)).

## Reconnect

Subscriptions are not restored after a dropped connection: the iterator raises
`NetworkError`, and the next subscription opens a new connection (and re-authenticates
it). Loop over the subscription:

```python
import asyncio
from typed_gtrade import GTrade, NetworkError

async with GTrade.new() as client:
  while True:
    try:
      async with client.trading.streams.orders() as frames:
        async for frame in frames:
          print(frame['snapshot'], frame['data'])
    except NetworkError:
      await asyncio.sleep(1)  # then subscribe again
```

Each new subscription starts with a fresh snapshot, but updates pushed while disconnected
are not replayed: re-read what you need (`account.fills`, for example) after reconnecting.

See the upstream [WebSocket guide](https://docs.gains.trade/developer/trading-api/websocket)
and [price feed guide](https://docs.gains.trade/developer/integrators/price-feed).
