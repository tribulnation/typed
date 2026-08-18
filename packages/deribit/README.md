# Typed Deribit

> A fully typed, validated async client for the Deribit API.

```python
from deribit import Deribit

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

## Documentation

- [API Keys Setup](https://tribulnation.com/typed/deribit/api-keys)
- [How To](https://tribulnation.com/typed/deribit/how-to)
- [Reference](https://tribulnation.com/typed/deribit/reference)

## How To

- [Fetch Market Data](https://tribulnation.com/typed/deribit/how-to/fetch-market-data)
- [Manage Account Data](https://tribulnation.com/typed/deribit/how-to/manage-account-data)
- [Place & Manage Orders](https://tribulnation.com/typed/deribit/how-to/place-and-manage-orders)
- [Manage Deposits & Withdrawals](https://tribulnation.com/typed/deribit/how-to/manage-deposits-and-withdrawals)
- [Paginate Through Results](https://tribulnation.com/typed/deribit/how-to/paginate-through-results)
- [Listen To Streams](https://tribulnation.com/typed/deribit/how-to/listen-to-streams)

## Source Code

> [github.com/tribulnation/deribit](https://github.com/tribulnation/deribit)
