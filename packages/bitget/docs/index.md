# Typed Bitget

> A fully typed, validated async client for the Bitget API.

```python
from bitget import Bitget

async with Bitget.new(public=True) as client:
  tickers = await client.uta.market.tickers(category='SPOT', symbol='BTCUSDT')
  print(tickers)
```

Bitget runs two live API generations on the same account host: **Classic v2** (`client.classic`),
the long-standing per-product API, and **UTA v3** (`client.uta`), Bitget's unified-account
generation and the one Bitget recommends for new integrations. A Bitget account is either
Classic-mode or UTA-mode, never both, so use whichever surface matches your account. This client
covers both, plus their independent WebSocket feeds (`client.classic_streams` /
`client.uta_streams`). The examples below use UTA.

## Why Typed Bitget?

- **🎯 Precise Types**: typed inputs and responses across both the Classic v2 and UTA v3 REST
  surfaces, not `dict`/`Any`.
- **✅ Runtime Validation**: every response validated against Bitget's real wire shapes by
  default.
- **⚡ Async First**: async HTTP plus four independent WebSocket connections (Classic/UTA ×
  public/private), built for concurrent workflows.
- **📚 Full Surface**: spot, margin, futures, earn, copy trading, P2P, broker, and tax, across
  both API generations, not just the popular endpoints.

## Installation

```bash
pip install typed-bitget
```

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Listen To Streams](how-to/listen-to-streams.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Manage Account Data](how-to/manage-account-data.md)
- [Manage Earn Instruments](how-to/manage-earn-instruments.md)
- [Manage Deposits & Withdrawals](how-to/manage-deposits-and-withdrawals.md)
- [Paginate Through Results](how-to/paginate-through-results.md)

## Reference

- [API Keys Setup](api-keys.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Bitget follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
