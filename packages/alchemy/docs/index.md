# Typed Alchemy

> A fully typed, validated async client for the Alchemy API.

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  prices = await client.prices.by_symbol(symbols=['ETH', 'BTC'])
  transfers = await client.transfers('ethereum').get_asset_transfers({
    'fromBlock': '0x0',
    'toAddress': '0x5c43B1eD97e52d009611D89b74fA829FE4ac56b1',
    'category': ['external'],
    'maxCount': '0x2',
  })
```

## Why Typed Alchemy?

- **🎯 Precise Types**: Typed request and response models across Portfolio, Prices, NFT, Token, Transfers, Utility, and Simulation endpoints.
- **✅ Runtime Validation**: Responses validated by default, not just typed on paper.
- **⚡ Async First**: One shared async HTTP transport, ready for concurrent requests.
- **📚 Full Surface**: Every supported network exposed uniformly, not just Ethereum.

## Installation

```bash
pip install typed-alchemy
```

## How To

- [Look Up Token Prices](how-to/look-up-token-prices.md)
- [Inspect Wallet Portfolio](how-to/inspect-wallet-portfolio.md)
- [Query NFTs](how-to/query-nfts.md)
- [Get Asset Transfers](how-to/get-asset-transfers.md)
- [Paginate Through Results](how-to/paginate-through-results.md)
- [Advanced RPC Methods](how-to/advanced-rpc-methods.md)
- [Streaming Support Status](how-to/listen-to-streams.md)

## Reference

- [API Keys Setup](api-keys.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Alchemy follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
