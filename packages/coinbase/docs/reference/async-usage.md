# Async Usage

Coinbase clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine — the underlying transports open lazily on first use.

```python
from typed_coinbase import Coinbase

client = Coinbase.new(public=True)
product = await client.app.advanced_trade.http.products.public.get('BTC-USD')
print(product['price'])
```

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of the block.

```python
from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  product = await client.app.advanced_trade.http.products.public.get('BTC-USD')
  book = await client.app.advanced_trade.http.products.public.book(product_id='BTC-USD', limit=50)
```

`Coinbase.new(...)` is the only thing the caller ever enters directly. It builds a single
`app`, composing `accounts` and `advanced_trade` — the latter itself composing `http` and
`streams`, with `streams` composing `market_data` and `user` — so every transport bottoms
out underneath that one call and the caller never separately enters a sub-client.

This is the recommended style for:

- multiple requests in the same flow
- long-lived sessions
- any streaming workflow
- code where explicit cleanup matters

## Streams

`market_data` (public) and `user` (private) both return a subscription manager from their
stream methods, not a stream directly. Use `async with` on it so the subscription
unsubscribes automatically when the block exits:

```python
from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  async with client.app.advanced_trade.streams.market_data.ticker(['BTC-USD']) as ticker:
    async for message in ticker:
      print(message['events'])
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  orders = await client.app.advanced_trade.streams.user.orders()
  async for message in orders:
    print(message['events'])
    break
  await orders.unsubscribe()
```

## Composite Client

`Coinbase.new(...)` builds a single `app`, which composes:

- `app.accounts` — Coinbase App v2, over HTTP
- `app.advanced_trade` — Advanced Trade v3, itself composing:
  - `app.advanced_trade.http` — the v3 REST surface
  - `app.advanced_trade.streams` — the v3 WebSocket surface, composing `market_data`
    (public channels) and `user` (private channels)

`app.accounts` and `app.advanced_trade.http` share one HTTP transport, since both v2 and v3
sit on the same host and are authenticated the same way. `app.advanced_trade.streams.market_data`
and `.user` each open their own WebSocket connection, since Coinbase serves public and
private streams on different hosts. `async with Coinbase.new(...)` enters every transport
concurrently and closes them all together at the end of the block.

## Guidance

Use direct construction for quick reads.

Use `async with` by default when:

- you are doing more than one call
- you are opening streams
- you want predictable cleanup
