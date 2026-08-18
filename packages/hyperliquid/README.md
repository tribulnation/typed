<p align="center">
  <a href="https://tribulnation.com/typed/hyperliquid">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tribulnation/hyperliquid/refs/heads/main/media/hyperliquid-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tribulnation/hyperliquid/refs/heads/main/media/hyperliquid-light.svg">
      <img alt="Typed Hyperliquid" src="https://raw.githubusercontent.com/tribulnation/hyperliquid/refs/heads/main/media/hyperliquid-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Hyperliquid API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-hyperliquid/">
    <img src="https://img.shields.io/pypi/v/typed-hyperliquid.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-hyperliquid/">
    <img src="https://img.shields.io/pypi/pyversions/typed-hyperliquid.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/hyperliquid/">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-hyperliquid.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/hyperliquid](https://tribulnation.com/typed/hyperliquid)
- **Source Code**: [https://github.com/tribulnation/hyperliquid](https://github.com/tribulnation/hyperliquid)

---

```python
from hyperliquid import Hyperliquid

async with Hyperliquid.ws(public=True) as client:
  stream = await client.streams.trades('BTC')
  async for msg in stream:
    for trade in msg:
      print(trade['px'], trade['sz'], trade['side'])
```

## Why Typed Hyperliquid?

- **🎯 Precise Types**: Typed endpoint inputs and responses, not `dict`/`Any`.
- **✅ Runtime Validation**: Responses validated by default, not just typed on paper.
- **⚡ Async First**: HTTP, request-response WebSocket, and subscription streams, built for
  concurrent workflows.
- **📚 Full Surface**: `client.info`, `client.exchange`, and `client.streams` -- perps,
  spot, and every documented info/exchange/stream endpoint, not just the popular ones.

## Installation

```bash
pip install typed-hyperliquid
```

## How To

- [Place & Manage Orders](https://tribulnation.com/typed/hyperliquid/how-to/place-and-manage-orders)
- [Fetch Market Data](https://tribulnation.com/typed/hyperliquid/how-to/fetch-market-data)
- [Fetch Your Balances & Positions](https://tribulnation.com/typed/hyperliquid/how-to/fetch-balances-and-positions)
- [Fetch Your Transactions](https://tribulnation.com/typed/hyperliquid/how-to/fetch-transactions)
- [Listen To Your Trades](https://tribulnation.com/typed/hyperliquid/how-to/listen-to-your-trades)
- [Listen To Public Data](https://tribulnation.com/typed/hyperliquid/how-to/listen-to-public-data)

## Reference

- [Authenticated Setup](https://tribulnation.com/typed/hyperliquid/authenticated-setup)
- [Async Usage](https://tribulnation.com/typed/hyperliquid/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/hyperliquid/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/hyperliquid/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/hyperliquid/reference/timestamps)
