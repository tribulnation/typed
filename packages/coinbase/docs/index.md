# Typed Coinbase

> A fully typed, validated async client for the Coinbase API.

```python
from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  product = await client.app.advanced_trade.http.products.public.get('BTC-USD')
  print(product['price'])
```

## Why Typed Coinbase?

- **🎯 Precise Types**: every endpoint's inputs and responses are typed, from Coinbase App (v2) wallets to Advanced Trade (v3) order configurations and fee tiers, not `dict`/`Any`.
- **✅ Runtime Validation**: every response is validated against its declared schema by default, across both the v2 and v3 APIs.
- **⚡ Async First**: async HTTP and WebSocket streaming, built for concurrent workflows across `app.accounts`, `app.advanced_trade.http`, and its two WebSocket connections.
- **📚 Full Surface**: every documented Coinbase App and Advanced Trade endpoint, not just the popular ones.

## Installation

```bash
pip install typed-coinbase
```

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Manage Account Data](how-to/manage-account-data.md)
- [Deposits & Withdrawals](how-to/deposits-and-withdrawals.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Listen To Streams](how-to/listen-to-streams.md)
- [Paginate Through Results](how-to/paginate-through-results.md)

## Reference

- [API Keys Setup](api-keys.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Coinbase follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
