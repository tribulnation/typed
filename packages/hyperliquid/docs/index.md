# Typed Hyperliquid

> A fully typed, validated async client for the Hyperliquid API.

```python
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new(public=True) as client:
  async with client.streams.trades('BTC') as trades:
    async for msg in trades:
      for trade in msg:
        print(trade['px'], trade['sz'], trade['side'])
```

## Why Typed Hyperliquid?

- **🎯 Precise Types**: Typed endpoint inputs and responses, not `dict`/`Any`.
- **✅ Runtime Validation**: Responses validated by default, not just typed on paper.
- **⚡ Async First**: HTTP, request-response WebSocket, and subscription streams, built for concurrent workflows.
- **📚 Full Surface**: `client.info`, `client.exchange`, and `client.streams` -- perps, spot, and every documented info/exchange/stream endpoint, not just the popular ones.

## Installation

```bash
pip install typed-hyperliquid
```

## How To

- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Fetch Market Data](how-to/fetch-market-data.md)
- [Fetch Your Balances & Positions](how-to/fetch-balances-and-positions.md)
- [Fetch Your Transactions](how-to/fetch-transactions.md)
- [Listen To Your Trades](how-to/listen-to-your-trades.md)
- [Listen To Public Data](how-to/listen-to-public-data.md)

## Reference

- [Authenticated Setup](authenticated-setup.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)
