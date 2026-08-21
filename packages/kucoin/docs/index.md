# Typed KuCoin

A fully typed, validated async client for the [KuCoin](https://www.kucoin.com) API: Spot,
Margin, Futures, Earn, VIP Lending, Affiliate, Convert, Copy Trading, Broker, and both
public and private WebSocket feeds.

```python
from typed_kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  ticker = await client.spot.ticker(symbol='BTC-USDT')
  print(ticker['price'])
```

## Why Typed KuCoin?

- **🎯 Precise Types**: every request and response across Spot, Margin, Futures and Earn is
  a typed structure, not a bare `dict`.
- **✅ Runtime Validation**: responses are checked against their schema by default, not just
  typed on paper.
- **⚡ Async First**: one client shares an HTTP connection pool per KuCoin host (default,
  futures, broker) and lazily opens the Spot/Margin WebSocket connection only when a stream
  is used.
- **📚 Full Surface**: Account, Spot, Margin, Futures, Earn, VIP Lending, Affiliate, Convert,
  Copy Trading and Broker each hang off their own attribute on `KuCoin`, alongside the
  Spot/Margin public and private WebSocket feeds.

## Installation

```bash
pip install typed-kucoin
```

## Quickstart

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  accounts = await client.account.spot_accounts()
  print(accounts)
```

`KuCoin.new()` reads `KUCOIN_API_KEY`, `KUCOIN_API_SECRET` and `KUCOIN_API_PASSPHRASE` from
the environment. Pass `public=True` for a credential-free client restricted to public
endpoints — see [API Keys Setup](api-keys.md).

## Client Surface

`client.account`, `client.spot`, `client.margin`, `client.earn`, `client.vip_lending`,
`client.affiliate`, `client.convert`, `client.futures`, `client.copy_trading` and
`client.broker` cover REST. `client.streams.spot_margin` and `client.streams.futures`
cover WebSocket (each is public and private topics on one connection) — see
[Listen To Streams](how-to/listen-to-streams.md).

## Documentation

- [API Keys Setup](api-keys.md)
- [How To](how-to/index.md)
- [Reference](reference/index.md)

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Listen To Streams](how-to/listen-to-streams.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Manage Account Data](how-to/manage-account-data.md)
- [Query & Manage Earn Instruments](how-to/manage-earn.md)
- [Deposits & Withdrawals](how-to/manage-deposits-and-withdrawals.md)
- [Paginate Through Results](how-to/paginate-through-results.md)

## Reference

- [API Keys Setup](api-keys.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed KuCoin follows the principles outlined in
[this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
