# Typed Coinbase

> A fully typed, validated async client for the Coinbase API — Coinbase App (v2) and Advanced Trade (v3), REST and WebSocket, one CDP API Key.

```python
from coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  product = await client.advanced_trade.products.public.get('BTC-USD')
  print(product['price'])
```

## Why Typed Coinbase?

- **🎯 Precise Types**: every endpoint's inputs and responses are typed, from Coinbase App (v2) wallets to Advanced Trade (v3) order configurations and fee tiers, not `dict`/`Any`.
- **✅ Runtime Validation**: every response is validated against its declared schema by default, across both the v2 and v3 APIs.
- **⚡ Async First**: async HTTP and WebSocket streaming, built for concurrent workflows against `accounts`, `advanced_trade`, and the public/private streams.
- **📚 Full Surface**: every documented Coinbase App and Advanced Trade endpoint, not just the popular ones.

## Installation

```bash
pip install typed-coinbase
```

## Surface

- `accounts` — Coinbase App v2: wallets, transaction history, sends, fiat deposits/withdrawals, receive addresses.
- `advanced_trade` — Advanced Trade v3: products, orders, portfolios, fees, convert, payment methods.
- `market_data` — public WebSocket channels: ticker, candles, order book, trades, status.
- `user` — private WebSocket channels: order and futures/position updates.

## Documentation

- [API Keys Setup](api-keys.md)
- [How To](how-to/index.md)
- [Reference](reference/index.md)

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Manage Account Data](how-to/manage-account-data.md)
- [Deposits & Withdrawals](how-to/deposits-and-withdrawals.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Listen To Streams](how-to/listen-to-streams.md)
- [Paginate Through Results](how-to/paginate-through-results.md)

## Design Philosophy

Typed Coinbase follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
