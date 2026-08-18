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

- [Fetch Wallet Data](https://tribulnation.com/typed/moralis/how-to/fetch-wallet-data)
- [Fetch Token Data](https://tribulnation.com/typed/moralis/how-to/fetch-token-data)
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
