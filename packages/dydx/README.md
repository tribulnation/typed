<p align="center">
  <a href="https://dydx.tribulnation.com">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tribulnation/dydx/refs/heads/main/media/dydx-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tribulnation/dydx/refs/heads/main/media/dydx-light.svg">
      <img alt="Typed dYdX" src="https://raw.githubusercontent.com/tribulnation/dydx/refs/heads/main/media/dydx-light.svg" width="360">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the dYdX Indexer, Node, Cosmos gRPC, and CometBFT APIs.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-dydx/">
    <img src="https://img.shields.io/pypi/v/typed-dydx.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-dydx/">
    <img src="https://img.shields.io/pypi/pyversions/typed-dydx.svg" alt="Python versions">
  </a>
  <a href="https://dydx.tribulnation.com/">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-dydx.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://dydx.tribulnation.com](https://dydx.tribulnation.com)
- **Source Code**: [https://github.com/tribulnation/dydx](https://github.com/tribulnation/dydx)

---

```python
from dydx import Dydx

async with Dydx.testnet(public=True) as client:
  market = await client.indexer.data.get_market('BTC-USD')
  stream = await client.indexer.streams.candles('ETH-USD', resolution='1MIN')
  async for candle in stream:
    await stream.unsubscribe()
  balances = await client.chain.bank.all_balances('dydx1...')
  block = await client.chain.comet.block()
  result = await client.node.place_order(market, order={
    'side': 'BUY',
    'size': '0.0001',
    'price': '50000',
    'flags': 'LONG_TERM'
  })
```

## Why Typed dYdX?

- **🎯 Precise Types**: Typed endpoint inputs and responses across dYdX services.
- **✅ Runtime Validation**: Validated Indexer and Comet responses by default.
- **⚡ Async First**: HTTP, WebSocket streams, gRPC queries, and transaction helpers.
- **📚 Full dYdX Surface**: `client.indexer`, `client.chain`, and `client.node`.

## Installation

```bash
pip install typed-dydx
```

## How To

- [Place & Manage Orders](https://dydx.tribulnation.com/how-to/place-and-manage-orders/)
- [Fetch Market Data](https://dydx.tribulnation.com/how-to/fetch-market-data/)
- [Manage Account Data](https://dydx.tribulnation.com/how-to/manage-account-data/)
- [Query Chain State](https://dydx.tribulnation.com/how-to/query-chain-state/)
- [Inspect Blocks & Transactions](https://dydx.tribulnation.com/how-to/inspect-blocks-and-transactions/)
- [Listen To Streams](https://dydx.tribulnation.com/how-to/listen-to-streams/)
- [Paginate Through Results](https://dydx.tribulnation.com/how-to/paginate-through-results/)

## Reference

- [Wallet Setup](https://dydx.tribulnation.com/api-keys/)
- [Error Handling](https://dydx.tribulnation.com/reference/error-handling/)
- [Environment Variables](https://dydx.tribulnation.com/reference/env-vars/)
