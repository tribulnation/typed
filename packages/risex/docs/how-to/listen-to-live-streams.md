# Listen To Live Streams

`client.streams` is the RISEx WebSocket feed. Every channel shares one connection, opened on the first subscription. Each subscription's acknowledgement is available as `stream.reply`.

## Public Channels

| Method | Pushes |
| --- | --- |
| `orderbook(market_ids)` | a book snapshot per market, then incremental level updates with a CRC32 `checksum` |
| `trades(market_ids)` | every matched trade |
| `oracle(market_ids)` | mark and index prices each block, as integers scaled by 1e18 |
| `expected_funding_rate(market_ids)` | the predicted funding rate |

Omit `market_ids` to receive every market.

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  async with client.streams.orderbook([1]) as stream:
    async for message in stream:
      print(message['type'], message['data']['bids'][:1], message['data']['asks'][:1])
```

Frames carry `type` (`snapshot` or `update`), `channel` and `data`. Leaving the `async with` block unsubscribes.

To manage the subscription yourself, `await` it and unsubscribe explicitly:

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  stream = await client.streams.trades([1])
  print(stream.reply['status'])
  async for message in stream:
    print(message['data'])
    break
  await stream.unsubscribe()
```

## Account Channels

These need the signer key (see [Authenticated Setup](../authenticated-setup.md)). The client authenticates the connection with it before subscribing, and again after a reconnect.

| Method | Pushes | Without a signer key |
| --- | --- | --- |
| `fills(market_ids)` | your fills | unavailable |
| `account()` | balances, equity, margin and risk: a snapshot, then updates | unavailable |
| `orders(market_ids, makers=...)` | an open-orders snapshot, then order lifecycle updates | every account's orders, optionally filtered by `makers` |
| `positions(market_ids, makers=...)` | your position updates | every account's positions, optionally filtered by `makers` |
| `funding(market_ids, makers=...)` | your funding payments | every account's payments, optionally filtered by `makers` |

```python
from typed_risex import RISEx

async with RISEx.new(network='testnet') as client:
  async with client.streams.orders([1]) as orders:
    async for message in orders:
      print(message['type'], message['data'])
```

## Changing A Channel's Filter

A client holds one subscription per channel. Subscribing to a channel that is already open raises `RuntimeError: Already subscribed to channel "<name>"`, so to change its markets (or `makers`), unsubscribe first, then subscribe with the new filter:

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  stream = await client.streams.orderbook([1])
  await stream.unsubscribe()
  async with client.streams.orderbook([2]) as stream:
    async for message in stream:
      print(message['data']['market_id'], message['data']['bids'][:1])
      break
```

To follow several markets at once, pass them all in one subscription: `client.streams.orderbook([1, 2])`.
