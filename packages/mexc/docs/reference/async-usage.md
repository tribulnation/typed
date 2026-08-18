# Async Usage

MEXC clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine — the underlying HTTP and WebSocket transports open lazily on first use.

```python
from mexc import MEXC

client = MEXC.public()
candles = await client.spot.market.candles(symbol='BTCUSDT', interval='1m', limit=5)
print(candles[-1][4])
```

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of the block.

```python
from mexc import MEXC

async with MEXC.public() as client:
  candles = await client.spot.market.candles(symbol='BTCUSDT', interval='1m', limit=5)
  contract_candles = await client.futures.market.candles('BTC_USDT', interval='Min1')
```

Entering the top-level client is the only thing you do. `MEXC.__aenter__` opens `client.spot`
and `client.futures` concurrently, and each of those opens its own `auth_http` and `streams`
the same way underneath — you never enter a sub-client yourself.

This is the recommended style for:

- multiple requests in the same flow
- long-lived sessions
- any streaming workflow
- code where explicit cleanup matters

## Streams

Both `client.spot.streams` and `client.futures.streams` exist, fully independent of each
other. Spot streams group into `market` (`depth`, `candles`, `trades`, `book_ticker`,
`book_ticker_batch`, `depth_updates`), `user`, and `listen_keys`. Futures streams group into
`market` and `user`.

Each stream method returns a `StreamManager`, not a stream directly. Use `async with` on it
so the subscription is unsubscribed automatically when the block exits:

```python
from mexc import MEXC

async with MEXC.public() as client:
  async with client.spot.streams.market.candles('BTCUSDT', 'Min1') as candles:
    async for kline in candles:
      print(kline.closing_price)
      break
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from mexc import MEXC

async with MEXC.public() as client:
  candles = await client.spot.streams.market.candles('BTCUSDT', 'Min1')
  async for kline in candles:
    print(kline.closing_price)
    break
  await candles.unsubscribe()
```

## Composite/Multi-Surface Client

`MEXC.new()`/`MEXC.public()` bundle two fully independent surfaces: `spot` and `futures`.
Each has its own `AuthHttpClient`, its own base URL, its own WebSocket URL, its own product
groups (`account`, `market`, `rebate`, `sub_accounts`, `trade`, `wallet` on spot;
`account`, `market`, `position`, `trade` on futures), and its own `streams`. Nothing is
shared between them — a spot API key and a futures API key are the same MEXC credentials,
but the two surfaces authenticate, connect, and disconnect independently.

```python
from mexc import MEXC

async with MEXC.public() as client:
  spot_candles = await client.spot.market.candles(symbol='BTCUSDT', interval='1m', limit=5)
  futures_candles = await client.futures.market.candles('BTC_USDT', interval='Min1')
```

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more than
one call, opening streams, or wanting predictable cleanup.
