# Async Usage

`typed_etherscan` is REST-only: one shared `httpx`-backed transport underneath all twelve
sections (`account`, `blocks`, `contracts`, `gas_tracker`, `l2`, `logs`, `nametags`,
`proxy`, `stats`, `tokens`, `transactions`, `usage`). There's no separate connection per
section to manage — entering the client opens the one connection pool every section calls
through.

## Quick Usage

You can call methods directly without a context manager; `Etherscan.new()` builds the
client and its transport eagerly:

```python
from typed_etherscan import Etherscan

client = Etherscan.new()
balance = await client.account.balance(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
```

## Context Manager Usage

`async with` is the recommended pattern — it closes the underlying HTTP connection pool on
exit:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  balance = await client.account.balance(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
```

Entering the top-level client is the only thing you do — every section
(`client.account`, `client.proxy`, `client.tokens`, ...) already shares that one client
instance, so there's no separate `async with client.account:` step.

## Guidance

- Prefer `async with` in scripts and services so the connection pool is always closed.
- Direct construction (`Etherscan.new()` with no context manager) is fine for a
  long-lived process that holds one client for its whole lifetime.
- There's no streaming transport here — every call is a single request/response.
