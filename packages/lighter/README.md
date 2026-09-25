<p align="center">
  <a href="https://tribulnation.com/typed/lighter">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://tribulnation.com/media/lockups/lighter-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://tribulnation.com/media/lockups/lighter-light.svg">
      <img alt="Typed Lighter" src="https://tribulnation.com/media/lockups/lighter-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Lighter API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-lighter/">
    <img src="https://img.shields.io/pypi/v/typed-lighter.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-lighter/">
    <img src="https://img.shields.io/pypi/pyversions/typed-lighter.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/lighter">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-lighter.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/lighter](https://tribulnation.com/typed/lighter)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/lighter](https://github.com/tribulnation/typed/tree/main/packages/lighter)

---

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  books = await client.api.markets.order_books(filter='perp')
  for book in books['order_books'][:5]:
    print(book['market_id'], book['symbol'], book['supported_price_decimals'])
```

[Lighter](https://apidocs.lighter.xyz/) is a perpetuals and spot order book running on its own
ZK rollup. Every state change (orders, transfers, leverage, API keys) is a signed L2
transaction; everything else is a REST read, a WebSocket stream, or an auth-token-gated
account write. The client mirrors that split:

| Surface | What it covers | Credentials |
|---|---|---|
| `client.api` | REST: markets, candles, accounts, orders and trades, transfers, blocks, pools, referrals, RFQ | public, or an auth token for private reads |
| `client.tx` | Signed transactions: orders, cancels, leverage, margin, transfers, sub-accounts, API keys, pools, staking | API key |
| `client.streams` | WebSocket channels: order books, trades, candles, market stats, account orders, positions, notifications | public, or an auth token for private channels |
| `client.signer` | Local signing with no network: every transaction type, auth tokens, key generation | API key |
| `client.explorer` | The public block explorer (mainnet and testnet): blocks, batches, logs, account history | none |
| `client.deposit_bridge` | Universal deposit addresses from other chains | bridge API key |

Signing happens in pure Python, inside the package: no compiled library, no external
process. Transactions go over HTTP or over the shared WebSocket connection, chosen per call.

## Authenticated Quick Start

```python
from typed_lighter import Lighter

async with Lighter.new() as client:  # reads LIGHTER_ACCOUNT_INDEX, LIGHTER_API_KEY_INDEX, LIGHTER_API_PRIVATE_KEY
  account = client.signer.account_index
  orders = await client.api.account.orders.active(account_index=account)
  for order in orders['orders']:
    print(order['market_index'], order['order_index'], order['price'], order['status'])
```

Create the API key on Lighter's [API keys page](https://app.lighter.xyz/apikeys): connect
your wallet, click **Generate API Key**, pick an index from `4` to `254`, and copy the private
key (it is shown once). The same page shows your account index. See
[Authenticated Setup](https://tribulnation.com/typed/lighter/authenticated-setup) for the
full walkthrough, read-only tokens and registering keys from code.

## Why Typed Lighter?

- **🎯 Precise Types**: Typed requests and responses on every surface, down to order-type unions and `Literal` statuses, not `dict`/`Any`.
- **✅ Runtime Validation**: REST replies, WebSocket frames and transaction receipts validated by default, not just typed on paper.
- **⚡ Async First**: Async HTTP and one multiplexed WebSocket connection for streams and transactions, built for concurrent workflows.
- **📚 Full Surface**: Every REST endpoint and stream channel, all 20 user transaction types, the explorer and the deposit bridge, not just the popular ones.

## Installation

```bash
pip install typed-lighter
```

## How To

- [Fetch Market Data](https://tribulnation.com/typed/lighter/how-to/fetch-market-data)
- [Fetch Account Data](https://tribulnation.com/typed/lighter/how-to/fetch-account-data)
- [Paginate Through Results](https://tribulnation.com/typed/lighter/how-to/paginate-through-results)
- [Place & Manage Orders](https://tribulnation.com/typed/lighter/how-to/place-and-manage-orders)
- [Listen To Streams](https://tribulnation.com/typed/lighter/how-to/listen-to-streams)
- [Batch Transactions](https://tribulnation.com/typed/lighter/how-to/batch-transactions)
- [Transfers & Sub-Accounts](https://tribulnation.com/typed/lighter/how-to/transfers-and-sub-accounts)
- [Sign Offline](https://tribulnation.com/typed/lighter/how-to/sign-offline)

## Reference

- [Authenticated Setup](https://tribulnation.com/typed/lighter/authenticated-setup)
- [Async Usage](https://tribulnation.com/typed/lighter/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/lighter/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/lighter/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/lighter/reference/timestamps)
- [Numbers](https://tribulnation.com/typed/lighter/reference/numbers)

## Design Philosophy

Typed Lighter follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
