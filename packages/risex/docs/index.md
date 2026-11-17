# Typed RISEx

> A fully typed, validated async client for the RISEx API.

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  markets = await client.markets.all()
  book = await client.markets.orderbook(market_id=1, limit=5)
  print(markets['markets'][0]['config']['name'], book['bids'][0]['price'])
```

## Why Typed RISEx?

- **🎯 Precise Types**: Typed requests and responses for every REST endpoint and WebSocket channel, with order bodies typed as limit/market unions, not `dict`/`Any`.
- **✅ Runtime Validation**: Responses validated by default, with prices and amounts as `Decimal` (or `''` where RISEx sends no value, and raw 10^18-scaled `int`s where it returns on-chain values; a few affiliate, leaderboard and points amounts with no observed value stay `str`), and timestamps as `datetime` with a few exceptions (see [Timestamps](reference/timestamps.md)).
- **⚡ Async First**: Async HTTP and a single multiplexed WebSocket feed, with EIP-712 permits, nonces and JWT sessions signed for you.
- **📚 Full Surface**: The full trading, account and market-data API: markets, orders, TP/SL, positions and margin, portfolio, signers and sessions, points, competition and leaderboard reads, and stats.

## Installation

```bash
pip install typed-risex
```

## Setup

RISEx has no API keys: you trade with an EVM account key plus a registered signer (session) key. See [Authenticated Setup](authenticated-setup.md) to create both on testnet, claim test USDC, and register the signer.

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Manage Leverage & Margin](how-to/manage-leverage-and-margin.md)
- [Paginate Through Results](how-to/paginate-through-results.md)
- [Listen To Live Streams](how-to/listen-to-live-streams.md)

## Reference

- [Authenticated Setup](authenticated-setup.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed RISEx follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
