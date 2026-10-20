# Typed Extended

> A fully typed, validated async client for the Extended API.

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  stats = await client.info.market_stats('BTC-USD')
  print(stats['lastPrice'], stats['markPrice'], stats['fundingRate'])
```

## Why Typed Extended?

- **🎯 Precise Types**: Typed inputs and responses for every REST call and WebSocket stream, including the order request union (limit, market, conditional, TP/SL).
- **✅ Runtime Validation**: Responses and stream messages validated by default, with prices and sizes as exact `Decimal` and timestamps as `datetime`.
- **⚡ Async First**: Async HTTP and WebSocket streams, with Stark order, transfer and withdrawal signing done for you.
- **📚 Full Surface**: Market data, account, orders, transfers and withdrawals, portfolio analytics, vault, interest, points, referrals and builder endpoints.

## Installation

```bash
pip install typed-extended
```

Signing runs in pure Python out of the box. For roughly 10x faster signatures, install the
optional native backend:

```bash
pip install "typed-extended[fast]"
```

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Listen To Live Streams](how-to/listen-to-live-streams.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Paginate Through Results](how-to/paginate-through-results.md)
- [Transfer & Withdraw](how-to/transfer-and-withdraw.md)

## Reference

- [Authenticated Setup](authenticated-setup.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Extended follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
