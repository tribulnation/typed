# Async Usage

Typed Nado is async-first and supports two usage styles:

- construct a client with `Nado.new()` and call methods directly, for quick one-off reads
- enter it with `async with`, so every connection it opened is closed at the end of the block

## Quick Usage

Constructing a client opens nothing. The shared HTTP connection pool and both WebSockets
connect on first use, so a script can build a client and call it straight away:

```python
from typed_nado import Nado

client = Nado.new(public=True)
print(await client.gateway.status())
```

Without `async with`, nothing closes the HTTP pool or sockets for you; that is fine for a
short script that exits right after.

## Context Manager Usage

`async with` is the recommended style for anything longer-lived, and for any streaming:

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  status = await client.gateway.status()
  candles = await client.archive.candlesticks(product_id=2, granularity=60, limit=10)
# HTTP pool and both WebSockets are closed here
```

Entering the top-level `Nado` client is the only thing you do. Every service under it
(`gateway`, `trigger`, `archive`, `rewards`, `gateway_v2`, `archive_v2`, `streams`) uses
transports the root owns, and each connects lazily the first time it is used. You never
enter a sub-surface separately.

## Gateway Over HTTP Or WebSocket

Every `client.gateway` method takes `transport='http'` (the default) or `transport='ws'`:

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  over_http = await client.gateway.market_price(2)
  over_ws = await client.gateway.market_price(2, transport='ws')
```

The gateway WebSocket answers one request at a time, in order, so concurrent `ws` calls
queue behind each other. Use HTTP (the default) for concurrent requests, and `ws` when you
want a warm connection for latency-sensitive sequences such as place-then-cancel. The
trigger, archive, rewards and v2 services are HTTP only.

## Concurrency

HTTP calls share one connection pool and run concurrently:

```python
import asyncio
from typed_nado import Nado

async with Nado.new(public=True) as client:
  btc, eth, symbols = await asyncio.gather(
    client.gateway.market_price(2),
    client.gateway.market_price(4),
    client.gateway.symbols(),
  )
```

## Streams

All subscriptions share one subscriptions WebSocket, opened on the first subscription and
closed with the client. Use `async with` on a stream to unsubscribe automatically:

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  async with client.streams.trade(2) as trades:
    async for trade in trades:
      print(trade['price'] / 10**18)
      break
  # unsubscribed here
```

Or await it and unsubscribe yourself:

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  trades = await client.streams.trade(2)
  async for trade in trades:
    print(trade['price'] / 10**18)
    break
  await trades.unsubscribe()
```

The private `order_update` stream authenticates the connection once, on its first
subscription; Nado allows 5 authenticated connections per wallet, and one client uses one.

## Guidance

- Build one client per process and reuse it; it holds a single HTTP pool and at most two
  sockets.
- Prefer `async with Nado.new(...) as client:` whenever you do more than one call or open
  a stream.
- Leave `transport` at `'http'` unless you specifically want the gateway WebSocket.
