# Typed Moralis

> A fully typed, validated async client for the Moralis API.

```python
from moralis import Moralis

async with Moralis.new() as client:
  balances = await client.evm.wallet.token_balances(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  print(balances['result'])
```

## Why Typed Moralis?

- **🎯 Precise Types**: Typed endpoint inputs and responses, not `dict`/`Any`.
- **✅ Runtime Validation**: Responses validated by default, not just typed on paper.
- **⚡ Async First**: Async HTTP, built for concurrent wallet and token lookups.
- **📚 Full Surface**: `client.evm.wallet` and `client.evm.token` cover every implemented
  Moralis EVM Data API endpoint, not just the popular ones.

## Installation

```bash
pip install typed-moralis
```

## How To

- [Fetch Wallet Data](how-to/fetch-wallet-data.md)
- [Fetch Token Data](how-to/fetch-token-data.md)
- [Paginate Through Results](how-to/paginate-through-results.md)

## Reference

- [API Keys Setup](api-keys.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Moralis follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
