# Async Usage

Alchemy clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine — the underlying HTTP
transport opens lazily on first use.

```python
from typed_alchemy import Alchemy

client = Alchemy.new()
prices = await client.prices.by_symbol(symbols=['ETH', 'BTC'])
print(prices['data'][0]['prices'])
```

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end of
the block. This is the recommended style for multiple requests, long-lived sessions, or code
where explicit cleanup matters.

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  prices = await client.prices.by_symbol(symbols=['ETH', 'BTC'])
  balances = await client.portfolio.token_balances(
    addresses=[{'address': '0x5c43B1eD97e52d009611D89b74fA829FE4ac56b1', 'networks': ['eth-mainnet']}],
  )
```

`client.portfolio` and `client.prices` are global groups; `client.nft(network=...)`,
`client.token(network=...)`, `client.transfers(network=...)`, `client.utility(network=...)`, and
`client.simulation(network=...)` are network-scoped groups. Every one of them shares the single
HTTP transport opened by the top-level `async with Alchemy.new(...)` block — there is nothing
else to enter separately, whichever combination of groups and networks you call.

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more than one
call or wanting predictable cleanup.

## HTTP Timeouts and Proxies

Pass a configured `typed_core.http.HttpClient` to control HTTP requests:

```python
from typed_core.http import HttpClient
from typed_alchemy import Alchemy

http = HttpClient(timeout=30, proxy="http://localhost:8080")
client = Alchemy.new(api_key="your-api-key", http=http)
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
