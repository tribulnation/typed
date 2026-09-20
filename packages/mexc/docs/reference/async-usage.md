# Async Usage

MEXC clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine — the underlying HTTP and WebSocket transports open lazily on first use.

```python
from typed_mexc import MEXC

client = MEXC.new(public=True)
candles = await client.spot.http.market.candles(symbol='BTCUSDT', interval='1m', limit=5)
print(candles[-1][4])
```

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of the block.

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  candles = await client.spot.http.market.candles(symbol='BTCUSDT', interval='1m', limit=5)
  contract_candles = await client.futures.http.market.candles('BTC_USDT', interval='Min1')
```

Entering the top-level client is the only thing you do. `MEXC.__aenter__` opens `client.spot`
and `client.futures` concurrently, and each of those opens its own REST transport and public
streams connection the same way underneath — you never enter a sub-client yourself. Each
product's own private (listen-key or login-gated) stream connection stays lazy either way,
opening only on the first real subscribe call, since opening it does real, credentialed
network work rather than the cheap no-op every other transport's own `__aenter__` is.

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
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  async with client.spot.streams.market.candles('BTCUSDT', 'Min1') as candles:
    async for kline in candles:
      print(kline.closing_price)
      break
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  candles = await client.spot.streams.market.candles('BTCUSDT', 'Min1')
  async for kline in candles:
    print(kline.closing_price)
    break
  await candles.unsubscribe()
```

## Composite/Multi-Surface Client

`MEXC.new()` bundles two fully independent surfaces: `spot` and `futures`.
Each has its own REST transport, its own base URL, its own WebSocket URL, its own product
groups (`account`, `listen_keys`, `market`, `rebate`, `sub_accounts`, `trade`, `wallet` on
spot; `account`, `market`, `position`, `trade` on futures), and its own `streams`. Nothing is
shared between them — a spot API key and a futures API key are the same MEXC credentials,
but the two surfaces authenticate, connect, and disconnect independently.

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  spot_candles = await client.spot.http.market.candles(symbol='BTCUSDT', interval='1m', limit=5)
  futures_candles = await client.futures.http.market.candles('BTC_USDT', interval='Min1')
```

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more than
one call, opening streams, or wanting predictable cleanup.

## HTTP Timeouts and Proxies

Pass a configured `typed_core.http.HttpClient` to control HTTP requests:

```python
from typed_core.http import HttpClient
from typed_mexc import MEXC

http = HttpClient(timeout=30, proxy="http://localhost:8080")
client = MEXC.new(public=True, http=http)
```

Use the resulting client with `async with client:`; exiting closes its HTTP transport,
including a supplied transport. Share it among surfaces within one client, and give
independently managed clients separate transports.

`timeout` defaults to five seconds of network inactivity. Pass `None` to disable it,
or an `httpx.Timeout` to configure connect, read, write, and pool timeouts separately.
Direct `HttpClient.request(..., timeout=...)` calls can override the default per request.
Requests are single-attempt; callers decide whether and when to retry.

Without an explicit `proxy`, HTTPX reads `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and
`NO_PROXY` from the environment. An explicit `proxy` overrides that environment routing,
including `NO_PROXY`. `HttpClient(trust_env=False)` disables HTTPX environment settings
(including certificate settings); an explicit proxy still applies. For HTTPS destinations,
a proxy URL commonly starts with `http://` because the proxy tunnels the TLS connection.

These settings configure HTTP requests, including HTTP-based authentication, and do not
configure WebSocket connections or gRPC calls.
