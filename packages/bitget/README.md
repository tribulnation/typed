<p align="center">
  <a href="https://tribulnation.com/typed/bitget">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/bitget/media/bitget-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/bitget/media/bitget-light.svg">
      <img alt="Typed Bitget" src="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/bitget/media/bitget-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Bitget API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-bitget/">
    <img src="https://img.shields.io/pypi/v/typed-bitget.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-bitget/">
    <img src="https://img.shields.io/pypi/pyversions/typed-bitget.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/bitget">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-bitget.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/bitget](https://tribulnation.com/typed/bitget)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/bitget](https://github.com/tribulnation/typed/tree/main/packages/bitget)

---

```python
from bitget import Bitget

async with Bitget.new(public=True) as client:
  tickers = await client.uta.market.tickers(category='SPOT', symbol='BTCUSDT')
  print(tickers)
```

Bitget runs two live API generations on the same account host: **Classic v2** (`client.classic`),
the long-standing per-product API, and **UTA v3** (`client.uta`), Bitget's unified-account
generation and the one Bitget recommends for new integrations. A Bitget account is either
Classic-mode or UTA-mode, never both, so use whichever surface matches your account. This client
covers both, plus their independent WebSocket feeds (`client.classic_streams` /
`client.uta_streams`). The examples below use UTA.

## Why Typed Bitget?

- **🎯 Precise Types**: typed inputs and responses across both the Classic v2 and UTA v3 REST
  surfaces, not `dict`/`Any`.
- **✅ Runtime Validation**: every response validated against Bitget's real wire shapes by
  default.
- **⚡ Async First**: async HTTP plus four independent WebSocket connections (Classic/UTA ×
  public/private), built for concurrent workflows.
- **📚 Full Surface**: spot, margin, futures, earn, copy trading, P2P, broker, and tax, across
  both API generations, not just the popular endpoints.

## Installation

```bash
pip install typed-bitget
```

## How To

- [Fetch Market Data](https://tribulnation.com/typed/bitget/how-to/fetch-market-data)
- [Listen To Streams](https://tribulnation.com/typed/bitget/how-to/listen-to-streams)
- [Place & Manage Orders](https://tribulnation.com/typed/bitget/how-to/place-and-manage-orders)
- [Manage Account Data](https://tribulnation.com/typed/bitget/how-to/manage-account-data)
- [Manage Earn Instruments](https://tribulnation.com/typed/bitget/how-to/manage-earn-instruments)
- [Manage Deposits & Withdrawals](https://tribulnation.com/typed/bitget/how-to/manage-deposits-and-withdrawals)
- [Paginate Through Results](https://tribulnation.com/typed/bitget/how-to/paginate-through-results)

## Reference

- [API Keys Setup](https://tribulnation.com/typed/bitget/api-keys)
- [Async Usage](https://tribulnation.com/typed/bitget/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/bitget/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/bitget/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/bitget/reference/timestamps)

## Design Philosophy

Typed Bitget follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
