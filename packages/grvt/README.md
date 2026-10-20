# Typed GRVT

<p align="center">
  <em>A fully typed, validated async client for the GRVT API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-grvt/">
    <img src="https://img.shields.io/pypi/v/typed-grvt.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-grvt/">
    <img src="https://img.shields.io/pypi/pyversions/typed-grvt.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/grvt">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-grvt.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/grvt](https://tribulnation.com/typed/grvt)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/grvt](https://github.com/tribulnation/typed/tree/main/packages/grvt)

---

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
| `client.trading` | Orders, fills, positions, account summaries, transfers, withdrawals, leverage, RFQs, vault summaries, redemption queues and redemption cancels | API key (+ signer key for `create_order`, `bulk_orders`, `transfer`, `withdrawal` and `set_derisk_mm_ratio`) |
| `client.trading_streams` | Your orders, fills, positions, transfers, deposits and withdrawals, live | API key |
| `client.edge` | Deposit addresses, bridge withdrawal quotes and status, referrals, strategies | API key (none for `investment_strategies` and `rhino_chain_id`) |

## How To

- [Fetch Market Data](https://tribulnation.com/typed/grvt/how-to/fetch-market-data)
- [Fetch Account Data](https://tribulnation.com/typed/grvt/how-to/fetch-account-data)
- [Place & Manage Orders](https://tribulnation.com/typed/grvt/how-to/place-and-manage-orders)
- [Paginate Through Results](https://tribulnation.com/typed/grvt/how-to/paginate-through-results)
- [Listen To Live Streams](https://tribulnation.com/typed/grvt/how-to/listen-to-live-streams)
- [Manage Transfers & Withdrawals](https://tribulnation.com/typed/grvt/how-to/manage-transfers-and-withdrawals)

## Reference

- [API Keys Setup](https://tribulnation.com/typed/grvt/api-keys)
- [Async Usage](https://tribulnation.com/typed/grvt/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/grvt/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/grvt/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/grvt/reference/timestamps)

## Design Philosophy

Typed GRVT follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
