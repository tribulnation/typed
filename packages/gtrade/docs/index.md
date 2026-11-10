# Typed gTrade

> A fully typed, validated async client for gTrade by Gains Network.

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  prices = await client.trading.markets.prices()
  btc = next(p for p in prices if p['market'] == 'BTC/USD')
  print(btc['mark'], btc['updatedAt'])
```

## Why Typed gTrade?

- **🎯 Precise Types**: Typed inputs and responses for the Trading API, the per-chain backend, Backend Global and pricing, not `dict`/`Any`.
- **✅ Runtime Validation**: Responses and stream frames validated by default, not just typed on paper.
- **⚡ Async First**: Async HTTP plus three WebSocket feeds (Trading API channels, backend contract events, live prices), built for concurrent workflows.
- **📚 Full Surface**: Every native Trading API endpoint and channel (markets, account, orders, positions, agents, API keys), plus the per-chain backend's trading-state reads and event stream, pricing, and a read subset of Backend Global (stats, history, leaderboards, contests, referrals).

## Installation

```bash
pip install typed-gtrade
```

## Surfaces

`GTrade.new(chain=...)` binds one chain and composes four surfaces:

| Attribute | Serves | Credentials |
| - | - | - |
| `client.trading` | The official Trading API: markets, account, orders, positions, agents, API keys, and its WebSocket channels (`client.trading.streams`) | None for market data, `system.*` and `agents.get`. None for `agents.create`, `agents.revoke` and `api_keys.issue` either: a master-wallet signature goes in the request. An agent key or read-only API key for private reads and channels; an agent key for order and position writes |
| `client.backend` | The chain's trading backend: trading variables, open trades, per-trader variables, and its contract-event stream (`client.backend.streams`) | None |
| `client.backend_global` | A read subset: protocol stats, trading history, trader history and stats, leaderboards, contests, referral reads | None |
| `client.pricing` | Price snapshots and the live price stream, indexed by `pairIndex` | None |

The Trading API serves Arbitrum (`chain='arbitrum'`, the default). On `base`, `polygon` and
`megaeth`, until it launches there, its REST calls other than `system.health` and
`system.ready` raise `BadRequest` (`CHAIN_NOT_FOUND`), and its channels raise
`NetworkError`. The per-chain backend covers `arbitrum`,
`base`, `polygon` and `megaeth`; `arbitrum-sepolia` targets the testnet deployment, whose
backend is live but whose Trading API host is currently unreachable. To use two chains,
build two clients. Backend Global and pricing are not chain-bound: Backend Global's stats,
trading-history and trader reads take an explicit `chain_id` (`42161` Arbitrum, `8453`
Base, `137` Polygon); its contests, referrals and `stats.total_supply` take none.

Numbers differ by surface: the Trading API returns `Decimal`, the per-chain backend mostly
raw contract-precision integers, Backend Global and pricing mostly floats. See
[Numbers & Precision](reference/numbers.md) for the exceptions.

Trading writes return an unsigned EVM transaction: the client never signs or broadcasts
transactions. See [Place & Manage Orders](how-to/place-and-manage-orders.md).

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Query Protocol Data](how-to/query-protocol-data.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Paginate Through Results](how-to/paginate-through-results.md)
- [Listen To Live Streams](how-to/listen-to-live-streams.md)

## Reference

- [Wallet & Agent Setup](authenticated-setup.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Numbers & Precision](reference/numbers.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed gTrade follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
