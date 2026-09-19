# Async Usage

Hyperliquid clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine.

The underlying HTTP and WebSocket transports open lazily on first use.

```python
from typed_hyperliquid import Hyperliquid

client = Hyperliquid.new(public=True)
mids = await client.info.all_mids()
print(mids['BTC'])
```

That works because the internal HTTP client creates its `httpx.AsyncClient` when the first request is sent.

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of the block.

```python
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new(public=True) as client:
  mids = await client.info.all_mids()
  book = await client.info.l2_book(coin='BTC')
```

This is the recommended style for:

- multiple requests in the same flow
- long-lived sessions
- any streaming workflow
- code where explicit cleanup matters

Entering the top-level client is the only thing you do -- `info`, `streams`, and `exchange`
each lazily enter their own transport as it's first used, not up front.

## Streams

Each `client.streams` method returns a subscription manager, not a stream directly. Use
`async with` on it so the subscription is unsubscribed automatically when the block exits:

```python
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new(public=True) as client:
  async with client.streams.trades('BTC') as trades:
    async for batch in trades:
      print(batch[0]['px'])
```

`await`ing the manager directly also works, but leaves the subscription open until you call
`unsubscribe()` yourself:

```python
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new(public=True) as client:
  trades = await client.streams.trades('BTC')
  async for batch in trades:
    print(batch[0]['px'])
    break
  await trades.unsubscribe()
```

## Composite Client

`Hyperliquid.new()` wires up all three surfaces at once -- there's no separate
transport-choice constructor:

- `client.info` -- always HTTP.
- `client.streams` -- always the shared WebSocket connection.
- `client.exchange` -- reachable over **both** transports on the same object: every signed
  trading method takes a `transport` keyword (`'http'`, the default, or `'ws'`), sending
  the identical call either as a plain HTTP POST or over the same WebSocket connection
  `streams` uses.

```python
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new() as client:
  mids = await client.info.all_mids()
  http_result = await client.exchange.noop()
  ws_result = await client.exchange.noop(transport='ws')
```

`Hyperliquid.new()` reads `HYPERLIQUID_PRIVATE_KEY` unless you pass a wallet explicitly.
`client.exchange` raises `AuthError` on access if the client was constructed with
`public=True` and no wallet was found.

## Guidance

Use direct construction for quick reads.

Use `async with` by default when:

- you are doing more than one call
- you are opening streams
- you want predictable cleanup

Pick `transport='http'` (the default) or `transport='ws'` per call based on whether you're
already holding the WebSocket connection open for streaming -- both sign and behave identically.

## HTTP Timeouts and Proxies

Pass a configured `typed_core.http.HttpClient` to control HTTP requests:

```python
from typed_core.http import HttpClient
from typed_hyperliquid import Hyperliquid

http = HttpClient(timeout=30, proxy="http://localhost:8080")
client = Hyperliquid.new(public=True, http=http)
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
