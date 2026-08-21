<p align="center">
  <a href="https://tribulnation.com/typed/moralis">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/moralis/media/moralis-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/moralis/media/moralis-light.svg">
      <img alt="Typed Moralis" src="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/moralis/media/moralis-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Moralis API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-moralis/">
    <img src="https://img.shields.io/pypi/v/typed-moralis.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-moralis/">
    <img src="https://img.shields.io/pypi/pyversions/typed-moralis.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/moralis">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-moralis.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/moralis](https://tribulnation.com/typed/moralis)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/moralis](https://github.com/tribulnation/typed/tree/main/packages/moralis)

---

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  balances = await client.evm.wallet.token_balances(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  print(balances['result'])
```

Moralis is a cross-chain wallet/token/NFT data API. This client covers its full surface
across seven product groups sharing one API key:

- `evm` -- wallet balances/history/net worth, ERC20 token metadata/price/holders, NFT
  metadata/ownership/prices/trades, and raw block/transaction lookups, across every EVM
  chain Moralis indexes
- `solana` -- wallet balances/portfolio and SPL token metadata/pricing
- `bitcoin` -- wallet balances/history, block/transaction lookups, and BTC pricing
- `universal` -- cross-chain entity search and chain/category market metrics
- `cortex` -- an AI chat endpoint over indexed on-chain data (deprecated upstream)
- `auth` -- Sign-In-With-Ethereum-style wallet challenge/verify flows
- `streams` -- webhook stream management (create, update, and inspect server-side
  push subscriptions; delivery is an HTTP POST to your own endpoint, not a client-side
  socket)

## Why Typed Moralis?

- **🎯 Precise Types**: Typed endpoint inputs and responses, not `dict`/`Any`.
- **✅ Runtime Validation**: Responses validated by default, not just typed on paper.
- **⚡ Async First**: Async HTTP, built for concurrent wallet, token, and NFT lookups.
- **📚 Full Surface**: every documented Moralis endpoint across EVM, Solana, Bitcoin,
  cross-chain, auth, and streams data -- not just the popular ones.

## Installation

```bash
pip install typed-moralis
```

## How To

- [Fetch Wallet Data](https://tribulnation.com/typed/moralis/how-to/fetch-wallet-data)
- [Fetch Token Data](https://tribulnation.com/typed/moralis/how-to/fetch-token-data)
- [Fetch NFT Data](https://tribulnation.com/typed/moralis/how-to/fetch-nft-data)
- [Fetch Solana Data](https://tribulnation.com/typed/moralis/how-to/fetch-solana-data)
- [Fetch Bitcoin Data](https://tribulnation.com/typed/moralis/how-to/fetch-bitcoin-data)
- [Explore Cross-Chain Data](https://tribulnation.com/typed/moralis/how-to/explore-cross-chain-data)
- [Authenticate a Wallet](https://tribulnation.com/typed/moralis/how-to/authenticate-a-wallet)
- [Manage Webhook Streams](https://tribulnation.com/typed/moralis/how-to/manage-webhook-streams)
- [Paginate Through Results](https://tribulnation.com/typed/moralis/how-to/paginate-through-results)

## Reference

- [API Keys Setup](https://tribulnation.com/typed/moralis/api-keys)
- [Async Usage](https://tribulnation.com/typed/moralis/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/moralis/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/moralis/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/moralis/reference/timestamps)

## Design Philosophy

Typed Moralis follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
