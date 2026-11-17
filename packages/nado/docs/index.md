# Typed Nado

> A fully typed, validated async client for the Nado API.

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  price = await client.gateway.market_price(2)  # BTC-PERP
  print(price['bid_x18'] / 10**18, price['ask_x18'] / 10**18)
```

Almost every read is public, including any subaccount's balances, orders and history. A
wallet key is needed for every signed call: placing, cancelling and replacing orders
(`gateway` and `trigger`), listing your trigger orders (`trigger.list_trigger_orders`, a
signed read), withdrawing and transferring collateral, minting and burning NLP, linking a
signer, liquidating a subaccount, registering for a trading competition, and the private
order-update stream — see [Authenticated Setup](authenticated-setup.md).

## Why Typed Nado?

- **🎯 Precise Types**: Typed inputs and responses across the gateway, trigger, archive, rewards and v2 market-data APIs, with x18 prices and amounts as real `int`s and timestamps as `datetime`s, not `dict`/`Any`.
- **✅ Runtime Validation**: Every REST response, WebSocket reply and stream event is validated by default, not just typed on paper.
- **⚡ Async First**: Async HTTP plus two WebSockets (gateway RPC and subscriptions), with a per-call `transport='http' | 'ws'` switch on every gateway method.
- **📚 Full Surface**: Every documented Nado endpoint — spot, perpetuals, trigger and TWAP orders, NLP vault, indexer history, rewards and streams — with EIP-712 signing built in.

## Installation

```bash
pip install typed-nado
```

## Services

| Attribute | What it covers |
| --- | --- |
| `client.gateway` | Live queries (products, prices, books, subaccounts, open orders) and signed executes (orders, cancels, withdrawals, transfers, NLP, linked signers) |
| `client.trigger` | Price-triggered and TWAP orders |
| `client.archive` | Indexed history: candles, matches, orders, events, funding, positions, snapshots |
| `client.rewards` | Airdrop and trading-competition leaderboards |
| `client.gateway_v2` | Aggregator-style assets, pairs, order book and APRs |
| `client.archive_v2` | Aggregator-style symbols, tickers, contracts and trades |
| `client.streams` | Live trades, book, candles, funding, liquidations, fills, positions and order updates |

`Nado.new()` targets mainnet (Ink); pass `network='testnet'` for Ink Sepolia.

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Paginate Through Results](how-to/paginate-through-results.md)
- [Listen To Live Streams](how-to/listen-to-live-streams.md)
- [Withdraw & Transfer Collateral](how-to/withdraw-and-transfer-collateral.md)
- [Use The NLP Vault](how-to/use-the-nlp-vault.md)

## Reference

- [Authenticated Setup](authenticated-setup.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Nado follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
