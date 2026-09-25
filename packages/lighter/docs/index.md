# Typed Lighter

> A fully typed, validated async client for the Lighter API.

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

See [Authenticated Setup](authenticated-setup.md) for how accounts, API keys and auth
tokens work on Lighter.

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

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Paginate Through Results](how-to/paginate-through-results.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Listen To Streams](how-to/listen-to-streams.md)
- [Batch Transactions](how-to/batch-transactions.md)
- [Transfers & Sub-Accounts](how-to/transfers-and-sub-accounts.md)
- [Sign Offline](how-to/sign-offline.md)

## Reference

- [Authenticated Setup](authenticated-setup.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)
- [Numbers](reference/numbers.md)

## Design Philosophy

Typed Lighter follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
