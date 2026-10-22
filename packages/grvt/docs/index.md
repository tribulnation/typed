# Typed GRVT

> A fully typed, validated async client for the GRVT API.

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  ticker = await client.market.ticker('BTC_USDT_Perp')
  print(ticker.get('mark_price'))
```

`Grvt.new()` connects to GRVT production. Pass `env='testnet'` (or `env='staging'`) to use a
test deployment instead.

## Why Typed GRVT?

- **🎯 Precise Types**: Typed orders, fills, positions and market data across perpetuals, futures, options, spot swaps and stable perpetuals, not `dict`/`Any`.
- **✅ Runtime Validation**: Every HTTP reply and WebSocket feed message is validated by default, with a per-call `validate` override.
- **⚡ Async First**: Async HTTP and JSON-RPC over WebSocket, with a per-call `transport` choice and live streams, built for concurrent workflows.
- **📚 Full Surface**: Market data, trading, account history, transfers, withdrawals, deposits, RFQs and vault summaries, with session login and EIP-712 signing handled for you.

## Installation

```bash
pip install typed-grvt
```

## Surfaces

| Attribute | What it covers | Credentials |
| --- | --- | --- |
| `client.market` | Instruments, currencies, tickers, order books, trades, candles, funding rates | none |
| `client.market_streams` | Live tickers, order books, trades and candles | none |
| `client.trading` | Orders, fills, positions, account summaries, transfers, withdrawals, leverage and isolated margin, RFQs, vault summaries, redemption queues and redemption cancels | API key (+ signer key for `create_order`, `bulk_orders`, `transfer`, `withdrawal`, `set_derisk_mm_ratio`, `set_position_config` and `add_position_margin`) |
| `client.trading_streams` | Your orders, fills, positions, transfers, deposits and withdrawals, live | API key |
| `client.edge` | Deposit addresses, bridge withdrawal quotes and status, referrals, strategies | API key (none for `investment_strategies` and `rhino_chain_id`) |

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Fetch Account Data](how-to/fetch-account-data.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Paginate Through Results](how-to/paginate-through-results.md)
- [Listen To Live Streams](how-to/listen-to-live-streams.md)
- [Manage Transfers & Withdrawals](how-to/manage-transfers-and-withdrawals.md)

## Reference

- [API Keys Setup](api-keys.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed GRVT follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
