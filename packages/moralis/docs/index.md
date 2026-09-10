# Typed Moralis

> A fully typed, validated async client for the Moralis API.

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  balances = await client.evm.wallet.token_balances(
    address='0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
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

- [Fetch Wallet Data](how-to/fetch-wallet-data.md)
- [Fetch Token Data](how-to/fetch-token-data.md)
- [Fetch NFT Data](how-to/fetch-nft-data.md)
- [Fetch Solana Data](how-to/fetch-solana-data.md)
- [Fetch Bitcoin Data](how-to/fetch-bitcoin-data.md)
- [Explore Cross-Chain Data](how-to/explore-cross-chain-data.md)
- [Authenticate a Wallet](how-to/authenticate-a-wallet.md)
- [Manage Webhook Streams](how-to/manage-webhook-streams.md)
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
