# Typed Deribit

> A fully typed, validated async client for the Deribit API.

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  instruments = await client.http.market_data.get_instruments(
    currency='BTC', kind='future'
  )
  print(instruments)
```

## Why Typed Deribit?

- **🎯 Precise Types**: every request/reply method and channel subscription across
  `.http`, `.ws`, and `.streams` is typed, parameters and all — not `dict`/`Any`.
- **✅ Runtime Validation**: responses are validated against the real schema by default,
  not just typed on paper.
- **⚡ Async First**: async HTTP and WebSocket transports, with `.streams` running
  concurrently on its own dedicated connection.
- **📚 Full Surface**: every documented endpoint across `market_data`, `trading`,
  `account`, `wallet`, `block_rfq`, `block_trade`, `combo_books`, `matching_engine`,
  `session`, `subscription_management`, and `supporting` — not just the popular ones.

## Installation

```bash
pip install typed-deribit
```

## How To

- [Fetch Market Data](how-to/fetch-market-data.md)
- [Manage Account Data](how-to/manage-account-data.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Manage Deposits & Withdrawals](how-to/manage-deposits-and-withdrawals.md)
- [Paginate Through Results](how-to/paginate-through-results.md)
- [Listen To Streams](how-to/listen-to-streams.md)

## Reference

- [API Keys Setup](api-keys.md)
- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed Deribit follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
