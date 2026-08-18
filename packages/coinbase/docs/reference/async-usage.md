# Async Usage

Coinbase clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine — the underlying transports open lazily on first use.

```python
from coinbase import Coinbase

client = Coinbase.new(public=True)
product = await client.advanced_trade.products.public.get('BTC-USD')
print(product['price'])
```

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of the block.

```python
from coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  product = await client.advanced_trade.products.public.get('BTC-USD')
  book = await client.advanced_trade.products.public.book(product_id='BTC-USD', limit=50)
```

`Coinbase.new(...)` is the only thing the caller ever enters directly. `accounts`,
`advanced_trade`, `market_data`, and `user` each bottom out on their own transport
underneath that single call — the caller never separately enters a sub-client.

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
from coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  async with client.market_data.ticker(['BTC-USD']) as ticker:
    async for message in ticker:
      print(message['events'])
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from coinbase import Coinbase

async with Coinbase.new() as client:
  orders = await client.user.orders()
  async for message in orders:
    print(message['events'])
    break
  await orders.unsubscribe()
```

## Composite Client

`Coinbase.new(...)` bundles four independent surfaces:

- `accounts` — Coinbase App v2, over HTTP
- `advanced_trade` — Advanced Trade v3, over HTTP
- `market_data` — public WebSocket channels
- `user` — private WebSocket channels

`accounts` and `advanced_trade` share one HTTP transport, since both v2 and v3 sit on the
same host and are authenticated the same way. `market_data` and `user` each open their own
WebSocket connection, since Coinbase serves public and private streams on different hosts.
`async with Coinbase.new(...)` enters all four concurrently and closes all four together at
the end of the block.

## Guidance

Use direct construction for quick reads.

Use `async with` by default when:

- you are doing more than one call
- you are opening streams
- you want predictable cleanup
