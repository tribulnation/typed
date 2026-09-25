# Typed Aster

> A fully typed, validated async client for the Aster API.

```python
from typed_aster import Aster

async with Aster.new(public=True) as client:
  book = await client.futures.market.depth('BTCUSDT', limit=5)
  print(book['bids'][0])
```

One `Aster` client covers five surfaces:

- `client.futures`: perpetual futures
- `client.spot`: spot trading
- `client.prediction`: prediction markets
- `client.chain`: Aster Chain (staking, transfers, withdrawals, and on-chain reads by address)
- `client.bapi`: the web app's public API (every asset that can be deposited or withdrawn)

Public market data needs no credentials. Everything signed uses Aster's Pro API wallets. See
[Authenticated Setup](authenticated-setup.md).

## Why Typed Aster?

- **🎯 Precise Types**: Typed order unions and `datetime` timestamps across futures, spot, prediction and Aster Chain, not `dict`/`Any`. Prices and quantities Aster sends as strings are `Decimal`; the few amounts it sends as JSON numbers (Aster Chain balances such as `walletBalance`, withdrawal fee estimates, fee caps) are `float`.
- **✅ Runtime Validation**: Every REST, JSON-RPC and WebSocket response is validated by default, not just typed on paper.
- **⚡ Async First**: Async HTTP plus WebSocket market and user-data streams, built for concurrent workflows.
- **📚 Full Surface**: Every documented Pro API endpoint, including strategy orders, sub-accounts, builders, prediction outcomes and staking.

## Installation

```bash
pip install typed-aster
```

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Paginate Through Results](how-to/paginate-through-results.md)
- [Listen To Live Streams](how-to/listen-to-live-streams.md)
- [Trade Prediction Markets](how-to/trade-prediction-markets.md)
- [Stake ASTER](how-to/stake-aster.md)
- [Manage Deposits & Withdrawals](how-to/manage-deposits-withdrawals.md)

## Reference

- [Authenticated Setup](authenticated-setup.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Aster follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
