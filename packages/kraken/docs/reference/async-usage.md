# Async Usage

Kraken clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine -- the underlying transport(s)
open lazily on first use.

```python
from kraken import Kraken

client = Kraken.new(public=True)
ticker = await client.spot.market_data.ticker(pair='XBTUSD')
print(ticker)
```

That works because the REST client opens its underlying `httpx.AsyncClient` when the first
request is sent -- there's no separate connect step to forget.

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of
the block.

```python
from kraken import Kraken

async with Kraken.new(public=True) as client:
  ticker = await client.spot.market_data.ticker(pair='XBTUSD')
  book = await client.spot.market_data.pre_trade(symbol='BTC/USD')
```

`Kraken.new(...)` builds both top-level surfaces -- `spot` (REST) and `streams` (WebSocket)
-- and its `__aenter__` enters them concurrently (`asyncio.gather`), so `async with Kraken.new(...)`
is the only thing you need: every sub-surface underneath (`spot.account`, `spot.trading`,
`streams.market_data`, ...) bottoms out lazily on first use, the same as direct construction.
You never enter a sub-client separately.

This is the recommended style for:

- multiple requests in the same flow
- long-lived sessions
- any streaming workflow
- code where explicit cleanup matters

## Streams

`streams.market_data` and `streams.private` methods are channel subscriptions: each returns
a `StreamManager`, not a stream directly. Use `async with` on it so the subscription is
unsubscribed automatically when the block exits:

```python
from kraken import Kraken

async with Kraken.new(public=True) as client:
  async with client.streams.market_data.ticker(symbol=['BTC/USD']) as ticker:
    async for msg in ticker:
      for entry in msg['data']:
        print(entry['symbol'], entry['last'])
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from kraken import Kraken

async with Kraken.new(public=True) as client:
  ticker = await client.streams.market_data.ticker(symbol=['BTC/USD'])
  async for msg in ticker:
    print(msg['data'][0]['last'])
    break
  await ticker.unsubscribe()
```

`streams.trading` is different: its methods (`add_order`, `cancel_order`, `edit_order`, ...)
are plain WebSocket RPC calls, not subscriptions -- `await` them directly, the same as an
HTTP call:

```python
from kraken import Kraken

async with Kraken.new() as client:
  result = await client.streams.trading.add_order(
    order_type='limit', side='buy', order_qty=0.001,
    symbol='BTC/USD', limit_price=10_000,
  )
  print(result.get('order_id'))
```

## Composite/Multi-Surface Client

`Kraken.new()` bundles two independent top-level surfaces:

- `spot` -- REST, under `https://api.kraken.com`. One `HttpRpcClient` shared across
  five product groups exposed as `cached_property`s: `account`, `earn`, `funding`,
  `market_data`, `trading`. Public methods (like `market_data.ticker`) work with no
  credentials; private ones sign each request.
- `streams` -- WebSocket v2, over two separate connections. `market_client` connects to
  the public `wss://ws.kraken.com/v2` and backs `streams.market_data`. `private_client`
  connects to the authenticated `wss://ws-auth.kraken.com/v2` and backs both
  `streams.private` (account channel subscriptions) and `streams.trading` (order
  placement/cancellation RPCs) -- Kraken serves both over the same authenticated socket.

Pass `public=True` to build a client with no credentials, usable only for
`spot.market_data` and `streams.market_data`.

```python
from kraken import Kraken

async with Kraken.new() as client:
  ticker = await client.spot.market_data.ticker(pair='XBTUSD')
  result = await client.streams.trading.add_order(
    order_type='market', side='buy', order_qty=0.001, symbol='BTC/USD',
  )
```

Each subscription's `StreamManager` also supports `.map(f)`/`.filter(f)` to transform or
filter pushes before you iterate them, if you want a narrower or reshaped stream.

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more than
one call, opening streams, or wanting predictable cleanup.
