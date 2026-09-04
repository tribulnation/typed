<p align="center">
  <a href="https://tribulnation.com/typed/alchemy">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://tribulnation.com/media/lockups/alchemy-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://tribulnation.com/media/lockups/alchemy-light.svg">
      <img alt="Typed Alchemy" src="https://tribulnation.com/media/lockups/alchemy-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Alchemy API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-alchemy/">
    <img src="https://img.shields.io/pypi/v/typed-alchemy.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-alchemy/">
    <img src="https://img.shields.io/pypi/pyversions/typed-alchemy.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/alchemy">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-alchemy.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/alchemy](https://tribulnation.com/typed/alchemy)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/alchemy](https://github.com/tribulnation/typed/tree/main/packages/alchemy)

---

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  prices = await client.prices.by_symbol(symbols=['ETH', 'BTC'])
  transfers = await client.transfers(network='ethereum').get_asset_transfers(
    from_block='0x0',
    to_address='0x5c43B1eD97e52d009611D89b74fA829FE4ac56b1',
    category=['external'],
    max_count='0x2',
  )
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

- [Look Up Token Prices](https://tribulnation.com/typed/alchemy/how-to/look-up-token-prices)
- [Inspect Wallet Portfolio](https://tribulnation.com/typed/alchemy/how-to/inspect-wallet-portfolio)
- [Query NFTs](https://tribulnation.com/typed/alchemy/how-to/query-nfts)
- [Get Asset Transfers](https://tribulnation.com/typed/alchemy/how-to/get-asset-transfers)
- [Paginate Through Results](https://tribulnation.com/typed/alchemy/how-to/paginate-through-results)
- [Advanced RPC Methods](https://tribulnation.com/typed/alchemy/how-to/advanced-rpc-methods)
- [Streaming Support Status](https://tribulnation.com/typed/alchemy/how-to/listen-to-streams)

## Reference

- [API Keys Setup](https://tribulnation.com/typed/alchemy/api-keys)
- [Async Usage](https://tribulnation.com/typed/alchemy/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/alchemy/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/alchemy/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/alchemy/reference/timestamps)

## Design Philosophy

Typed Alchemy follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
