# Async Usage

Every RISEx call is a coroutine. There are two ways to hold a client:

- construct it with `RISEx.new(...)` and call methods directly, for a quick script
- enter it with `async with`, which closes the REST connection pool and the WebSocket connection on exit

## Quick Usage

```python
from typed_risex import RISEx

client = RISEx.new(public=True)
book = await client.markets.orderbook(market_id=1, limit=5)
print(book['bids'][0])
```

Connections open on first use. Without `async with`, nothing closes them for you.

## Context Manager Usage

```python
from typed_risex import RISEx

async with RISEx.new(network='testnet') as client:
  markets = await client.markets.all()
  fees = await client.account.fees()
```

Entering the top-level client is the only thing you do: `client.markets`, `client.orders`, `client.streams` and every other surface share its transports and open lazily as they are first used. You never enter a sub-surface separately. Entering opens no connection; the REST pool connects on the first request and the WebSocket on the first subscription.

## Streams

All channels share one WebSocket connection. Use `async with` on the subscription to unsubscribe automatically:

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  async with client.streams.oracle([1]) as stream:
    async for message in stream:
      print(message['data']['prices'])
      break
```

Or `await` the subscription and unsubscribe yourself:

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  stream = await client.streams.oracle([1])
  async for message in stream:
    print(message['data']['prices'])
    break
  await stream.unsubscribe()
```

## Concurrency

Requests are independent, so `asyncio.gather` works across any surfaces:

```python
import asyncio
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  markets, book, trades = await asyncio.gather(
    client.markets.all(),
    client.markets.orderbook(market_id=1),
    client.markets.trade_history(market_id=1, limit=10),
  )
```

Signed writes can also run concurrently: the client hands out permit nonces under a lock, and concurrent calls needing a login share a single one.

## Guidance

Use direct construction for one-off reads. Use `async with` for anything longer-lived, for streams, and whenever you want connections closed predictably.
