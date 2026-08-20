<p align="center">
  <a href="https://tribulnation.com/typed/binance">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/binance/media/binance-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/binance/media/binance-light.svg">
      <img alt="Typed Binance" src="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/binance/media/binance-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Binance API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-binance/">
    <img src="https://img.shields.io/pypi/v/typed-binance.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-binance/">
    <img src="https://img.shields.io/pypi/pyversions/typed-binance.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/binance">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-binance.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/binance](https://tribulnation.com/typed/binance)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/binance](https://github.com/tribulnation/typed/tree/main/packages/binance)

---

```python
from typed_binance import Binance

async with Binance.new(public=True) as client:
  price = await client.spot.http.market.ticker_price(symbol='BTCUSDT')
  print(price)
```

## Why Typed Binance?

- **🎯 Precise Types**: every spot, USD-M futures, COIN-M futures, options, and portfolio margin parameter and response is a precise Python type, not `dict`/`Any`.
- **✅ Runtime Validation**: every response is validated against its schema by default, not just typed on paper.
- **⚡ Async First**: async HTTP requests and WebSocket market-data streams, built for concurrent workflows across every product line.
- **📚 Full Surface**: every documented spot, futures, options, and portfolio margin endpoint, not just the popular ones.

## Installation

```bash
pip install typed-binance
```

## How To

- [Fetch Market Data](https://tribulnation.com/typed/binance/how-to/fetch-market-data) — public prices, order books, and candles
- [Listen To Streams](https://tribulnation.com/typed/binance/how-to/listen-to-streams) — subscribe to market data and account event streams
- [Place & Manage Orders](https://tribulnation.com/typed/binance/how-to/place-and-manage-orders) — submit, query, cancel, and list spot orders
- [Fetch Account Data](https://tribulnation.com/typed/binance/how-to/manage-account-data) — balances, positions, and trade history
- [Query & Manage Earn Instruments](https://tribulnation.com/typed/binance/how-to/manage-earn) — Simple Earn products, positions, subscribe, and redeem
- [Manage Deposits & Withdrawals](https://tribulnation.com/typed/binance/how-to/manage-deposits-and-withdrawals) — deposit addresses/history and withdrawals
- [Paginate Through Results](https://tribulnation.com/typed/binance/how-to/paginate-through-results) — walk a time range across multiple pages

## Reference

- [API Keys Setup](https://tribulnation.com/typed/binance/api-keys)
- [Async Usage](https://tribulnation.com/typed/binance/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/binance/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/binance/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/binance/reference/timestamps)

## Design Philosophy

Typed Binance follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
