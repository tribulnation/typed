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

- [Fetch Market Data](https://tribulnation.com/typed/binance/how-to/fetch-market-data) — public prices, order books, and candles
- [Listen To Streams](https://tribulnation.com/typed/binance/how-to/listen-to-streams) — subscribe to market data and account event streams
- [Place & Manage Orders](https://tribulnation.com/typed/binance/how-to/place-and-manage-orders) — submit, query, cancel, and list spot orders
- [Fetch Account Data](https://tribulnation.com/typed/binance/how-to/manage-account-data) — balances, positions, and trade history
- [Query & Manage Earn Instruments](https://tribulnation.com/typed/binance/how-to/manage-earn) — Simple Earn products, positions, subscribe, and redeem
- [Manage Deposits & Withdrawals](https://tribulnation.com/typed/binance/how-to/manage-deposits-and-withdrawals) — deposit addresses/history and withdrawals
- [Paginate Through Results](https://tribulnation.com/typed/binance/how-to/paginate-through-results) — walk a time range across multiple pages

## Documentation

- [API Keys Setup](https://tribulnation.com/typed/binance/api-keys)
- [How To](https://tribulnation.com/typed/binance/how-to)
- [Reference](https://tribulnation.com/typed/binance/reference)
