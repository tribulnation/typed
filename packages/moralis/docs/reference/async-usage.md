# Async Usage

Moralis clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine -- the underlying HTTP
connections open lazily on first use.

```python
from typed_moralis import Moralis

client = Moralis.new()
balances = await client.evm.wallet.token_balances(
  '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
)
print(balances['result'])
```

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end
of the block. This is the recommended style for multiple requests, long-lived sessions,
or code where explicit cleanup matters. Entering `Moralis.new(...)` is the only thing the
caller does -- there's no separate sub-client to enter.

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  balances = await client.evm.wallet.token_balances(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  metadata = await client.evm.token.metadata.token_metadata(
    chain='eth', addresses=['0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'],
  )
```

Moralis routes its 7 product groups (`evm`, `bitcoin`, `solana`, `universal`, `cortex`,
`auth`, `streams`) to 5 different hosts -- `evm`/`bitcoin`/`universal` share one, since
they're all served from Moralis's "deep-index" API. Entering the top-level client takes
ownership of all 5 transports up front; each still opens its actual HTTP connection
lazily, on that transport's own first request, exactly like Quick Usage above.

Moralis has no client-side streaming surface: `streams` manages server-side webhook
subscriptions over plain REST calls, not a socket you read from in Python, so there's no
`async for message in ...` pattern here.

Every call requires an API key: `Moralis.new()` raises `AuthError` immediately, before
any request is sent, unless `api_key` is passed or `MORALIS_API_KEY` is set. There is no
public, credential-free mode.

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more
than one call or when you want predictable cleanup.
