# Async Usage

Hyperliquid clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine.

The underlying HTTP and WebSocket clients open lazily on first use.

```python
from hyperliquid import Hyperliquid

client = Hyperliquid.http(public=True)
mids = await client.info.all_mids()
print(mids['BTC'])
```

That works because the internal HTTP client creates its `httpx.AsyncClient` when the first request is sent.

The same idea applies to request-response WebSocket usage:

```python
from hyperliquid import Hyperliquid

client = Hyperliquid.ws(public=True)
book = await client.info.l2_book(coin='BTC')
print(book['coin'])
```

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of the block.

```python
from hyperliquid import Hyperliquid

async with Hyperliquid.http(public=True) as client:
  mids = await client.info.all_mids()
  book = await client.info.l2_book(coin='BTC')
```

This is the recommended style for:

- multiple requests in the same flow
- long-lived sessions
- any streaming workflow
- code where explicit cleanup matters

## Streams

For `client.streams`, prefer `async with` almost always.

Subscriptions keep a WebSocket connection open until the client is closed.

```python
from hyperliquid import Hyperliquid

async with Hyperliquid.ws(public=True) as client:
  trades = await client.streams.trades('BTC')
  async for batch in trades:
    print(batch[0]['px'])
```

## Composite Client

`Hyperliquid.http()` and `Hyperliquid.ws()` bundle `info`, `exchange`, and `streams` together.

```python
from hyperliquid import Hyperliquid

async with Hyperliquid.http() as client:
  mids = await client.info.all_mids()
  result = await client.exchange.noop()
```

These convenience constructors read `HYPERLIQUID_PRIVATE_KEY` unless you pass a wallet explicitly.

Inside the composite client:

- `info` and `exchange` share one HTTP or request-response WebSocket transport
- `streams` uses its own subscription transport in `Hyperliquid.http()`
- all three are entered and exited together when you use `async with`

## Guidance

Use direct construction for quick reads.

Use `async with` by default when:

- you are doing more than one call
- you are opening streams
- you want predictable cleanup
