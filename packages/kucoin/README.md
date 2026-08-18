<p align="center">
  <a href="https://tribulnation.com/typed/kucoin">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/kucoin/media/kucoin-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/kucoin/media/kucoin-light.svg">
      <img alt="Typed KuCoin" src="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/kucoin/media/kucoin-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the KuCoin API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-kucoin/">
    <img src="https://img.shields.io/pypi/v/typed-kucoin.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-kucoin/">
    <img src="https://img.shields.io/pypi/pyversions/typed-kucoin.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/kucoin">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-kucoin.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/kucoin](https://tribulnation.com/typed/kucoin)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/kucoin](https://github.com/tribulnation/typed/tree/main/packages/kucoin)

---

```python
from kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  ticker = await client.spot.ticker(symbol='BTC-USDT')
  print(ticker['price'])
```

## Why Typed KuCoin?

- **🎯 Precise Types**: every request and response across Spot, Margin, Futures and Earn is
  a typed structure, not a bare `dict`.
- **✅ Runtime Validation**: responses are checked against their schema by default, not just
  typed on paper.
- **⚡ Async First**: one client shares an HTTP connection pool per KuCoin host (default,
  futures, broker) and lazily opens the Spot/Margin WebSocket connection only when a stream
  is used.
- **📚 Full Surface**: Account, Spot, Margin, Futures, Earn, VIP Lending, Affiliate, Convert,
  Copy Trading and Broker each hang off their own attribute on `KuCoin`, alongside the
  Spot/Margin public and private WebSocket feeds.

## Installation

```bash
pip install typed-kucoin
```

## How To

- [Fetch Market Data](https://tribulnation.com/typed/kucoin/how-to/fetch-market-data)
- [Listen To Streams](https://tribulnation.com/typed/kucoin/how-to/listen-to-streams)
- [Place & Manage Orders](https://tribulnation.com/typed/kucoin/how-to/place-and-manage-orders)
- [Manage Account Data](https://tribulnation.com/typed/kucoin/how-to/manage-account-data)
- [Query & Manage Earn Instruments](https://tribulnation.com/typed/kucoin/how-to/manage-earn)
- [Deposits & Withdrawals](https://tribulnation.com/typed/kucoin/how-to/manage-deposits-and-withdrawals)
- [Paginate Through Results](https://tribulnation.com/typed/kucoin/how-to/paginate-through-results)

## Reference

- [API Keys Setup](https://tribulnation.com/typed/kucoin/api-keys)
- [Async Usage](https://tribulnation.com/typed/kucoin/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/kucoin/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/kucoin/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/kucoin/reference/timestamps)

## Design Philosophy

Typed KuCoin follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
