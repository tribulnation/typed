# Async Usage

Bybit clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine — the underlying transports
open lazily on first use.

```python
from typed_bybit import Bybit

client = Bybit.new(public=True)
ticker = await client.http.market.tickers(category='spot', symbol='BTCUSDT')
print(ticker['list'][0]['lastPrice'])
```

## Context Manager Usage

`async with Bybit.new(...) as client:` is the only thing the caller does. Underneath it,
`client.http` (one shared HTTP connection pool) and all nine of `client.ws`'s WebSocket
connections (`spot`, `linear`, `inverse`, `option`, `spread`, `rfq`, `private`, `trade`,
`finance`) open concurrently, and every one of them closes cleanly on exit — the caller
never separately enters `client.http` or an individual `client.ws.*` connection.

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  candles = await client.http.market.kline(category='spot', symbol='BTCUSDT', interval='60')
  book = await client.http.market.orderbook(category='spot', symbol='BTCUSDT', limit=5)
```

Use `async with` by default for multiple requests, long-lived sessions, any streaming
workflow, or code where explicit cleanup matters.

## Streams

Bybit's WebSocket surface is nine separate connections, not one: seven public-category
channels (`spot`, `linear`, `inverse`, `option`, `spread`, `rfq`, `finance`), one private
channel (`private`), and one order-entry connection (`trade` — see below, it isn't a
subscription).

Each subscribe-shaped method on `client.ws.*` returns a `StreamManager`. Use `async with` on
it so the subscription is unsubscribed automatically when the block exits:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  async with client.ws.spot.orderbook(50, 'BTCUSDT') as book:
    async for update in book:
      print(update['s'], update['u'])
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  book = await client.ws.spot.orderbook(50, 'BTCUSDT')
  async for update in book:
    print(update['s'], update['u'])
    break
  await book.unsubscribe()
```

`client.ws.private.wallet()` works the same way, and needs credentials — see
[API Keys Setup](../api-keys.md).

## The WS Trade Connection

`client.ws.trade` is request/reply order entry, not a subscription — don't lump it in with
the streams above. `order_create(args)` builds and signs the `order.create` command frame; it
does not send it:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  frame = client.ws.trade.order_create({
    'category': 'spot', 'symbol': 'BTCUSDT',
    'side': 'Buy', 'orderType': 'Limit', 'qty': '0.001', 'price': '20000',
  })
  reply = await client.ws.trade.socket.rpc_request(frame)
```

Building the frame separately from sending it lets you inspect or compare a command's exact
wire shape without placing an order.

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more than
one call, opening streams, or wanting predictable cleanup.
