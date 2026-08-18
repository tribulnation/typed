# Typed dYdX

> A fully typed, validated async client for the dYdX Indexer, Node and CosmosSDK/CometBFT APIs.

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

- **🎯 Precise Types**: Typed endpoint inputs and responses.
- **✅ Runtime Validation**: Validated responses by default.
- **⚡ Async First**: Indexer HTTP, WebSocket streams, Cosmos gRPC, Comet RPC, and signed node transactions.
- **📚 Full dYdX Surface**: Market data, account history, chain state, blocks, transactions, and order placement.

## Installation

```bash
pip install typed-dydx
```

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Manage Account Data](how-to/manage-account-data.md)
- [Query Chain State](how-to/query-chain-state.md)
- [Inspect Blocks and Transactions](how-to/inspect-blocks-and-transactions.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Paginate Through Results](how-to/paginate-through-results.md)
- [Listen To Streams](how-to/listen-to-streams.md)

## Reference

- [Wallet Setup](api-keys.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
