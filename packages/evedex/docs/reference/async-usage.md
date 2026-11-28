# Async Usage

The EVEDEX client is async-only and supports two usage styles: calling methods on a freshly
built client for quick reads, or entering it with `async with` for explicit lifecycle
management, which is the recommended style:

```python
from typed_evedex import Evedex

async with Evedex.new(public=True) as client:
  info = await client.exchange.market.info()
```

## Quick Usage

For a quick one-off read you can also call methods without `async with`; the HTTP pool
opens lazily on first use. Connections are then not closed for you, so prefer the context
manager for anything longer-lived, and always for streams.

```python
from typed_evedex import Evedex

client = Evedex.new(public=True)
ping = await client.exchange.ping()
print(ping['time'])
```

## Context Manager Usage

Entering the top-level client with `async with` is the only thing you do. The client owns one
HTTP connection pool, shared by the Exchange, Auth and market-data services, and one
WebSocket connection, shared by every stream. Each opens lazily: the WebSocket connects on
the first subscription, and the wallet session signs in on the first private call. You never
enter `client.exchange`, `client.streams` or any other sub-surface yourself. Leaving the block
closes everything that was opened.

## Streams

Every stream method returns a subscription with two usage styles. With `async with`, the
channel is unsubscribed when the block exits:

```python
from typed_evedex import Evedex

async with Evedex.new(public=True) as client:
  async with client.streams.heartbeat() as stream:
    async for beat in stream:
      print(beat['t'])
      break
```

With `await`, you unsubscribe explicitly:

```python
from typed_evedex import Evedex

async with Evedex.new(public=True) as client:
  stream = await client.streams.recent_trades('BTCUSD')
  async for trade in stream:
    print(trade['fillPrice'])
    break
  await stream.unsubscribe()
```

Subscriptions share the client's single connection, so run several concurrently with
`asyncio.gather` or a task group.

## Composite Client

`Evedex` groups four surfaces, all sharing the same credentials and connections:

| Attribute | Service |
| --- | --- |
| `client.exchange` | Trading: market data, account, orders, positions, TP/SL, transfers, sub-accounts |
| `client.auth` | Sign-in session, wallet user, API keys, sub-accounts |
| `client.market_data` | Candle history |
| `client.streams` | WebSocket channels, public and `client.streams.account` |

## Guidance

Create one client per process and reuse it; it is safe to call concurrently. Use
`async with` so connections close predictably.

## HTTP Timeouts, Keep-Alive and Proxies

Pass a configured `typed_core.http.HttpClient` to control HTTP requests:

```python
from typed_core.http import HttpClient
from typed_evedex import Evedex

http = HttpClient(timeout=30, keepalive_expiry=120, proxy="http://localhost:8080")
client = Evedex.new(public=True, http=http)
```

The Exchange, Auth and market-data services and the wallet session all share the supplied
client. Use the resulting client with `async with client:`; exiting closes its HTTP
transport, including a supplied one. Give independently managed clients separate transports.

Without `http`, the client builds one with `Evedex.new(timeout=...)` (ten seconds by
default) as its request timeout. A supplied `HttpClient` keeps its own timeout; `timeout`
then applies only to the WebSocket connect. `keepalive_expiry` is how long an idle pooled
connection is kept for reuse (see `typed_core.http.HttpClient`). Requests are
single-attempt; callers decide whether and when to retry.

Without an explicit `proxy`, HTTPX reads `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`, and
`NO_PROXY` from the environment. An explicit `proxy` overrides that environment routing,
including `NO_PROXY`. `HttpClient(trust_env=False)` disables HTTPX environment settings
(including certificate settings); an explicit proxy still applies.

These settings configure HTTP requests, including the wallet sign-in, and do not configure
the WebSocket connection.
