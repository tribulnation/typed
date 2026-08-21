# Typed dYdX

> A fully typed, validated async client for the dYdX Indexer, Chain (Cosmos gRPC +
> CometBFT), and Node APIs.

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

- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Fetch Market Data](how-to/fetch-market-data.md)
- [Manage Account Data](how-to/manage-account-data.md)
- [Query Chain State](how-to/query-chain-state.md)
- [Inspect Blocks & Transactions](how-to/inspect-blocks-and-transactions.md)
- [Listen To Streams](how-to/listen-to-streams.md)
- [Paginate Through Results](how-to/paginate-through-results.md)

## Reference

- [Wallet Setup](authenticated-setup.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed dYdX follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
