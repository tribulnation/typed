<p align="center">
  <a href="https://tribulnation.com/typed/coinbase">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://tribulnation.com/media/lockups/coinbase-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://tribulnation.com/media/lockups/coinbase-light.svg">
      <img alt="Typed Coinbase" src="https://tribulnation.com/media/lockups/coinbase-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Coinbase API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-coinbase/">
    <img src="https://img.shields.io/pypi/v/typed-coinbase.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-coinbase/">
    <img src="https://img.shields.io/pypi/pyversions/typed-coinbase.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/coinbase">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-coinbase.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/coinbase](https://tribulnation.com/typed/coinbase)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/coinbase](https://github.com/tribulnation/typed/tree/main/packages/coinbase)

---

```python
from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  product = await client.app.advanced_trade.http.products.public.get('BTC-USD')
  print(product['price'])
```

## Why Typed Coinbase?

- **🎯 Precise Types**: every endpoint's inputs and responses are typed, from Coinbase App (v2) wallets to Advanced Trade (v3) order configurations and fee tiers, not `dict`/`Any`.
- **✅ Runtime Validation**: every response is validated against its declared schema by default, across both the v2 and v3 APIs.
- **⚡ Async First**: async HTTP and WebSocket streaming, built for concurrent workflows across `app.accounts`, `app.advanced_trade.http`, and its two WebSocket connections.
- **📚 Full Surface**: every documented Coinbase App and Advanced Trade endpoint, not just the popular ones.

## Installation

```bash
pip install typed-coinbase
```

## How To

- [Fetch Market Data](https://tribulnation.com/typed/coinbase/how-to/fetch-market-data)
- [Manage Account Data](https://tribulnation.com/typed/coinbase/how-to/manage-account-data)
- [Deposits & Withdrawals](https://tribulnation.com/typed/coinbase/how-to/deposits-and-withdrawals)
- [Place & Manage Orders](https://tribulnation.com/typed/coinbase/how-to/place-and-manage-orders)
- [Listen To Streams](https://tribulnation.com/typed/coinbase/how-to/listen-to-streams)
- [Paginate Through Results](https://tribulnation.com/typed/coinbase/how-to/paginate-through-results)

## Reference

- [API Keys Setup](https://tribulnation.com/typed/coinbase/api-keys)
- [Async Usage](https://tribulnation.com/typed/coinbase/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/coinbase/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/coinbase/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/coinbase/reference/timestamps)

## Design Philosophy

Typed Coinbase follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
