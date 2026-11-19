<p align="center">
  <a href="https://tribulnation.com/typed/nado">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://tribulnation.com/media/lockups/nado-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://tribulnation.com/media/lockups/nado-light.svg">
      <img alt="Typed Nado" src="https://tribulnation.com/media/lockups/nado-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Nado API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-nado/">
    <img src="https://img.shields.io/pypi/v/typed-nado.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-nado/">
    <img src="https://img.shields.io/pypi/pyversions/typed-nado.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/nado">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-nado.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/nado](https://tribulnation.com/typed/nado)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/nado](https://github.com/tribulnation/typed/tree/main/packages/nado)

---

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
order-update stream — see [Authenticated Setup](https://tribulnation.com/typed/nado/authenticated-setup).

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

- [Fetch Market Data](https://tribulnation.com/typed/nado/how-to/fetch-market-data)
- [Fetch Account Data](https://tribulnation.com/typed/nado/how-to/fetch-account-data)
- [Place & Manage Orders](https://tribulnation.com/typed/nado/how-to/place-and-manage-orders)
- [Paginate Through Results](https://tribulnation.com/typed/nado/how-to/paginate-through-results)
- [Listen To Live Streams](https://tribulnation.com/typed/nado/how-to/listen-to-live-streams)
- [Withdraw & Transfer Collateral](https://tribulnation.com/typed/nado/how-to/withdraw-and-transfer-collateral)
- [Use The NLP Vault](https://tribulnation.com/typed/nado/how-to/use-the-nlp-vault)

## Reference

- [Authenticated Setup](https://tribulnation.com/typed/nado/authenticated-setup)
- [Async Usage](https://tribulnation.com/typed/nado/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/nado/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/nado/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/nado/reference/timestamps)

## Design Philosophy

Typed Nado follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
