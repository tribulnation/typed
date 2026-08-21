<p align="center">
  <a href="https://tribulnation.com/typed/deribit">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/deribit/media/deribit-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/deribit/media/deribit-light.svg">
      <img alt="Typed Deribit" src="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/deribit/media/deribit-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Deribit API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-deribit/">
    <img src="https://img.shields.io/pypi/v/typed-deribit.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-deribit/">
    <img src="https://img.shields.io/pypi/pyversions/typed-deribit.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/deribit">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-deribit.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/deribit](https://tribulnation.com/typed/deribit)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/deribit](https://github.com/tribulnation/typed/tree/main/packages/deribit)

---

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

- [Fetch Market Data](https://tribulnation.com/typed/deribit/how-to/fetch-market-data)
- [Manage Account Data](https://tribulnation.com/typed/deribit/how-to/manage-account-data)
- [Place & Manage Orders](https://tribulnation.com/typed/deribit/how-to/place-and-manage-orders)
- [Manage Deposits & Withdrawals](https://tribulnation.com/typed/deribit/how-to/manage-deposits-and-withdrawals)
- [Paginate Through Results](https://tribulnation.com/typed/deribit/how-to/paginate-through-results)
- [Listen To Streams](https://tribulnation.com/typed/deribit/how-to/listen-to-streams)

## Reference

- [API Keys Setup](https://tribulnation.com/typed/deribit/api-keys)
- [Async Usage](https://tribulnation.com/typed/deribit/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/deribit/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/deribit/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/deribit/reference/timestamps)

## Design Philosophy

Typed Deribit follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
