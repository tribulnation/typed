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

## Documentation

- [API Keys Setup](https://tribulnation.com/typed/coinbase/api-keys)
- [How To](https://tribulnation.com/typed/coinbase/how-to)
- [Reference](https://tribulnation.com/typed/coinbase/reference)

## How To

- [Fetch Market Data](https://tribulnation.com/typed/coinbase/how-to/fetch-market-data)
- [Manage Account Data](https://tribulnation.com/typed/coinbase/how-to/manage-account-data)
- [Deposits & Withdrawals](https://tribulnation.com/typed/coinbase/how-to/deposits-and-withdrawals)
- [Place & Manage Orders](https://tribulnation.com/typed/coinbase/how-to/place-and-manage-orders)
- [Listen To Streams](https://tribulnation.com/typed/coinbase/how-to/listen-to-streams)
- [Paginate Through Results](https://tribulnation.com/typed/coinbase/how-to/paginate-through-results)

## Source Code

> [github.com/tribulnation/coinbase](https://github.com/tribulnation/coinbase)
