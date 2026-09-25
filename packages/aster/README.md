<p align="center">
  <a href="https://tribulnation.com/typed/aster">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://tribulnation.com/media/lockups/aster-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://tribulnation.com/media/lockups/aster-light.svg">
      <img alt="Typed Aster" src="https://tribulnation.com/media/lockups/aster-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Aster API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-aster/">
    <img src="https://img.shields.io/pypi/v/typed-aster.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-aster/">
    <img src="https://img.shields.io/pypi/pyversions/typed-aster.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/aster">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-aster.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/aster](https://tribulnation.com/typed/aster)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/aster](https://github.com/tribulnation/typed/tree/main/packages/aster)

---

```python
from typed_aster import Aster

async with Aster.new(public=True) as client:
  book = await client.futures.market.depth('BTCUSDT', limit=5)
  print(book['bids'][0])
```

One `Aster` client covers five surfaces:

- `client.futures`: perpetual futures
- `client.spot`: spot trading
- `client.prediction`: prediction markets
- `client.chain`: Aster Chain (staking, transfers, withdrawals, and on-chain reads by address)
- `client.bapi`: the web app's public API (every asset that can be deposited or withdrawn)

Public market data needs no credentials. Everything signed uses Aster's Pro API wallets. See
[Authenticated Setup](https://tribulnation.com/typed/aster/authenticated-setup).

## Why Typed Aster?

- **🎯 Precise Types**: Typed order unions and `datetime` timestamps across futures, spot, prediction and Aster Chain, not `dict`/`Any`. Prices and quantities Aster sends as strings are `Decimal`; the few amounts it sends as JSON numbers (Aster Chain balances such as `walletBalance`, withdrawal fee estimates, fee caps) are `float`.
- **✅ Runtime Validation**: Every REST, JSON-RPC and WebSocket response is validated by default, not just typed on paper.
- **⚡ Async First**: Async HTTP plus WebSocket market and user-data streams, built for concurrent workflows.
- **📚 Full Surface**: Every documented Pro API endpoint, including strategy orders, sub-accounts, builders, prediction outcomes and staking.

## Installation

```bash
pip install typed-aster
```

## How To

- [Fetch Market Data](https://tribulnation.com/typed/aster/how-to/fetch-market-data)
- [Fetch Account Data](https://tribulnation.com/typed/aster/how-to/fetch-account-data)
- [Place & Manage Orders](https://tribulnation.com/typed/aster/how-to/place-and-manage-orders)
- [Paginate Through Results](https://tribulnation.com/typed/aster/how-to/paginate-through-results)
- [Listen To Live Streams](https://tribulnation.com/typed/aster/how-to/listen-to-live-streams)
- [Trade Prediction Markets](https://tribulnation.com/typed/aster/how-to/trade-prediction-markets)
- [Stake ASTER](https://tribulnation.com/typed/aster/how-to/stake-aster)
- [Manage Deposits & Withdrawals](https://tribulnation.com/typed/aster/how-to/manage-deposits-withdrawals)

## Reference

- [Authenticated Setup](https://tribulnation.com/typed/aster/authenticated-setup)
- [Async Usage](https://tribulnation.com/typed/aster/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/aster/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/aster/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/aster/reference/timestamps)

## Design Philosophy

Typed Aster follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
