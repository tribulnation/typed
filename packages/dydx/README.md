<p align="center">
  <a href="https://tribulnation.com/typed/dydx">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/dydx/media/dydx-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/dydx/media/dydx-light.svg">
      <img alt="Typed dYdX" src="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/dydx/media/dydx-light.svg" width="360">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the dYdX Indexer, Chain (Cosmos gRPC + CometBFT), and Node APIs.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-dydx/">
    <img src="https://img.shields.io/pypi/v/typed-dydx.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-dydx/">
    <img src="https://img.shields.io/pypi/pyversions/typed-dydx.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/dydx">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-dydx.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/dydx](https://tribulnation.com/typed/dydx)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/dydx](https://github.com/tribulnation/typed/tree/main/packages/dydx)

---

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  market = await client.indexer.data.get_market('BTC-USD')
  candles = await client.indexer.streams.candles('ETH-USD', resolution='1MIN')
  async for candle in candles:
    print(candle)
    break
  await candles.unsubscribe()
  balances = await client.chain.bank.all_balances('dydx1...', resolve_denom=False)
  block = await client.chain.comet.block()
  result = await client.node.place_order(market, order={
    'side': 'BUY',
    'size': '0.0001',
    'price': '50000',
    'flags': 'LONG_TERM',
  })
```

## Why Typed dYdX?

- **🎯 Precise Types**: Typed inputs and responses across the Indexer, Chain, and Node surfaces.
- **✅ Runtime Validation**: Indexer and Comet responses validated by default.
- **⚡ Async First**: Indexer HTTP and WebSocket streams, Cosmos gRPC queries, and signed node transactions.
- **📚 Full Surface**: `client.indexer`, `client.chain`, and `client.node` cover market data, account history, chain state, and order placement.

## Installation

```bash
pip install typed-dydx
```

## How To

- [Place & Manage Orders](https://tribulnation.com/typed/dydx/how-to/place-and-manage-orders)
- [Fetch Market Data](https://tribulnation.com/typed/dydx/how-to/fetch-market-data)
- [Manage Account Data](https://tribulnation.com/typed/dydx/how-to/manage-account-data)
- [Query Chain State](https://tribulnation.com/typed/dydx/how-to/query-chain-state)
- [Inspect Blocks & Transactions](https://tribulnation.com/typed/dydx/how-to/inspect-blocks-and-transactions)
- [Listen To Streams](https://tribulnation.com/typed/dydx/how-to/listen-to-streams)
- [Paginate Through Results](https://tribulnation.com/typed/dydx/how-to/paginate-through-results)

## Reference

- [Wallet Setup](https://tribulnation.com/typed/dydx/authenticated-setup)
- [Async Usage](https://tribulnation.com/typed/dydx/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/dydx/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/dydx/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/dydx/reference/timestamps)

## Design Philosophy

Typed dYdX follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
