# Async Usage

Moralis clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows, plain construction is fine — the underlying HTTP
transport opens lazily on first use.

```python
from moralis import Moralis

client = Moralis.new()
balances = await client.evm.wallet.token_balances(
  '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
)
print(balances['result'])
```

## Context Manager Usage

Use `async with` when you want the client to open up front and close cleanly at the end
of the block. This is the recommended style for multiple requests, long-lived sessions,
or code where explicit cleanup matters.

```python
from moralis import Moralis

async with Moralis.new() as client:
  balances = await client.evm.wallet.token_balances(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  metadata = await client.evm.token.metadata(
    addresses=['0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'], chain='eth',
  )
```

`client.evm.wallet` and `client.evm.token` share the one HTTP transport the top-level
`async with` opens — entering `Moralis.new(...)` is the only thing the caller does.

Moralis has no streaming surface, so there is no Streams section here.

Every call requires an API key: `Moralis.new()` raises `AuthError` immediately, before
any request is sent, unless `api_key` is passed or `MORALIS_API_KEY` is set. There is no
public, credential-free mode.

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more
than one call or when you want predictable cleanup.
