# Typed Coinbase

> A fully typed, validated async client for the Coinbase API.

```python
from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  product = await client.app.advanced_trade.http.products.public.get('BTC-USD')
  print(product['price'])
```

Typed Coinbase covers two independent Coinbase product families under one client: **Coinbase App** (`client.app`, above — Consumer/Business v2 and Advanced Trade v3) and **Coinbase Exchange** (`client.exchange`, the institutional API formerly known as Pro/GDAX):

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  products = await client.exchange.http.products.list()
  print(products[0]['id'])
```

Each family has its own credentials, host, and setup guide — see [API Keys Setup](api-keys.md) for App and [Exchange API Keys Setup](exchange-api-keys.md) for Exchange.

`client.international` additionally provides public INTX instrument details, quotes and
funding history, without account credentials. Its native `BTC-PERP` symbol is
distinct from Advanced Trade's `BTC-PERP-INTX` product ID.

```python
from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  instrument = await client.international.instruments.get('BTC-PERP')
  print(instrument['quote']['mark_price'], instrument['open_interest'])
  page = await client.international.instruments.funding('BTC-PERP', result_limit=100)
  print(page['results'][0]['funding_rate'])
```

The response preserves the API's `pagination` and `results` fields. Funding rates
and mark prices are `Decimal`, and event times are aware `datetime` values.
`funding_paged` walks all retained rows through retryable offset pages; new events
can shift offsets, so a walk is not an atomic snapshot. INTX account endpoints are
not exposed by this namespace.
Instrument prices and quantities also use `Decimal`; margin ratios sent as JSON
numbers remain `float`. The instrument's `funding_interval` is an integer duration
in nanoseconds (zero for spot), while its quote's `timestamp` is an aware `datetime`.
For spot routing, `notional_24hr` and `avg_daily_notional` can be absent or the empty
string, which remains distinct from a reported numeric zero.

## Why Typed Coinbase?

- **🎯 Precise Types**: every endpoint's inputs and responses are typed, from Coinbase App's v2 wallets and Advanced Trade's v3 order configurations to Exchange's order book and order-lifecycle shapes, not `dict`/`Any`.
- **✅ Runtime Validation**: every response is validated against its declared schema by default, across App and Exchange alike.
- **⚡ Async First**: async HTTP and WebSocket streaming, built for concurrent workflows across `app`'s two WebSocket connections and Exchange's single WebSocket Feed.
- **📚 Full Surface**: every documented Coinbase App, Advanced Trade, and Coinbase Exchange endpoint, not just the popular ones.

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
- [Fetch Exchange Market Data](how-to/fetch-exchange-market-data.md)

## Reference

- [API Keys Setup](api-keys.md)
- [Exchange API Keys Setup](exchange-api-keys.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Coinbase follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
