# Typed Binance

> A fully typed, validated async client for the Binance API.

```python
from binance import Binance

async with Binance.new(public=True) as client:
  price = await client.spot.market.ticker_price(symbol='BTCUSDT')
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

- [Fetch Market Data](how-to/fetch-market-data.md) — public prices, order books, and candles
- [Listen To Streams](how-to/listen-to-streams.md) — subscribe to market data and account event streams
- [Place & Manage Orders](how-to/place-and-manage-orders.md) — submit, query, cancel, and list spot orders
- [Fetch Account Data](how-to/manage-account-data.md) — balances, positions, and trade history
- [Query & Manage Earn Instruments](how-to/manage-earn.md) — Simple Earn products, positions, subscribe, and redeem
- [Manage Deposits & Withdrawals](how-to/manage-deposits-and-withdrawals.md) — deposit addresses/history and withdrawals
- [Paginate Through Results](how-to/paginate-through-results.md) — walk a time range across multiple pages

## Reference

- [API Keys Setup](api-keys.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Binance follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
