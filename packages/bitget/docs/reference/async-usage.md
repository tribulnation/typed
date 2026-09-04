# Async Usage

Bitget clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine — the underlying transport(s)
open lazily on first use.

```python
from typed_bitget import Bitget

client = Bitget.new(public=True)
tickers = await client.uta.market.tickers(category='SPOT', symbol='BTCUSDT')
print(tickers)
```

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of
the block. This is the recommended style for multiple requests, long-lived sessions, any
streaming workflow, or code where explicit cleanup matters. Entering the top-level
`Bitget.new(...)` client is the only thing the caller does — `classic`, `uta`,
`classic_streams`, and `uta_streams` all enter underneath it.

```python
from typed_bitget import Bitget

async with Bitget.new(public=True) as client:
  symbols = await client.classic.spot.symbols()
  instruments = await client.uta.market.instruments(category='SPOT')
```

## Streams

Each streams method returns a subscription manager, not a stream directly. Use `async with`
on it so the subscription is unsubscribed automatically when the block exits:

```python
from typed_bitget import Bitget

async with Bitget.new(public=True) as client:
  async with client.uta_streams.orderbook('spot', symbol='BTCUSDT', depth='') as book:
    async for update in book:
      print(update['data'])
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from typed_bitget import Bitget

async with Bitget.new(public=True) as client:
  book = await client.uta_streams.orderbook('spot', symbol='BTCUSDT', depth='')
  async for update in book:
    print(update['data'])
    break
  await book.unsubscribe()
```

Both `classic_streams` and `uta_streams` also expose `authed_command` — a lower-latency,
id-correlated trade command (`classic_streams.order.place`, `classic_streams.order.cancel`)
sent over the private WebSocket connection and answered with a single reply, not a
subscription. Don't expect it to behave like the pub-sub methods above:

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  reply = await client.classic_streams.order.place(
    'SPOT', 'BTCUSDT',
    {'orderType': 'limit', 'side': 'buy', 'size': '0.001', 'force': 'gtc', 'price': '30000'},
  )
  print(reply['arg'][0]['params']['orderId'])
```

## Composite/Multi-Surface Client

`Bitget.new()` composes four independent surfaces: `classic` and `uta` (REST, Classic v2 and
UTA v3), and `classic_streams`/`uta_streams` (their independent WebSocket feeds). `classic`
and `uta` **share one `HttpRpcClient` instance** (`BitgetBase.http_client`,
`core/base.py`) — same host, envelope, and signing scheme either way — while the two
streaming surfaces each own a separate connection, since their wire shapes differ
structurally.

`__aenter__` gathers all three underlying transports concurrently (`BitgetBase.__aenter__`,
`core/base.py`). `typed_core`'s `HttpClient.client` lazily instantiates its underlying
`httpx.AsyncClient` under an `asyncio.Lock`, so entering `classic` and `uta` at the same time
is safe even though they share one HTTP client underneath.

```python
from typed_bitget import Bitget

async with Bitget.new(public=True) as client:
  # classic and uta share one HTTP client; classic_streams/uta_streams are independent WS connections
  symbols = await client.classic.spot.symbols()
  instruments = await client.uta.market.instruments(category='SPOT')
```

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more than
one call, opening streams, or wanting predictable cleanup.
