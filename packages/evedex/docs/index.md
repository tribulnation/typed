# Typed EVEDEX

> A fully typed, validated async client for the EVEDEX API.

```python
from typed_evedex import Evedex

async with Evedex.new(public=True) as client:
  book = await client.exchange.market.order_book(instrument='BTCUSD')
  print(book['bids'][0], book['asks'][0])
```

## Why Typed EVEDEX?

- **🎯 Precise Types**: Typed requests and responses for every EVEDEX perpetual endpoint, with prices and sizes as `Decimal` and times as `datetime`, not `dict`/`Any`.
- **✅ Runtime Validation**: Every HTTP response and WebSocket publication is validated by default, not just typed on paper.
- **⚡ Async First**: Async HTTP for the Exchange, Auth and market-data services and async Centrifugo streams, sharing one client.
- **📚 Full Surface**: Market data, account, orders (single and batch), positions, TP/SL, transfers, sub-accounts, API keys and every public and private channel, with EIP-712 signing built in.

## Installation

```bash
pip install typed-evedex
```

## Getting Started

Public market data needs no credentials: build the client with `public=True`, as above.
Reading your account needs an API key or your wallet's private key; trading needs the
private key, which signs every order. See [Authenticated Setup](authenticated-setup.md).

```python
from typed_evedex import Evedex

async with Evedex.new() as client:  # reads EVEDEX_PRIVATE_KEY / EVEDEX_API_KEY
  balance = await client.exchange.account.available_balance()
  print(balance['availableBalance'])
```

Pass `env='demo'` to use the EVEDEX demo environment (`evedex.io`) instead of production.

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Manage Positions & TP/SL](how-to/manage-positions.md)
- [Listen To Live Streams](how-to/listen-to-live-streams.md)
- [Paginate Through Results](how-to/paginate-through-results.md)

## Reference

- [Authenticated Setup](authenticated-setup.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed EVEDEX follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
