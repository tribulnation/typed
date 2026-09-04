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
