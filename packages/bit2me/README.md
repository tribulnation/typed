<p align="center">
  <a href="https://tribulnation.com/typed/bit2me">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/bit2me/media/bit2me-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/bit2me/media/bit2me-light.svg">
      <img alt="Typed Bit2Me" src="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/bit2me/media/bit2me-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Bit2Me API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-bit2me/">
    <img src="https://img.shields.io/pypi/v/typed-bit2me.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-bit2me/">
    <img src="https://img.shields.io/pypi/pyversions/typed-bit2me.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/bit2me">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-bit2me.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/bit2me](https://tribulnation.com/typed/bit2me)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/bit2me](https://github.com/tribulnation/typed/tree/main/packages/bit2me)

---

```python
from dotenv import load_dotenv
from typed_bit2me import Bit2Me

load_dotenv()

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()
  print(balances[0].get('currency'), balances[0].get('balance'))
```

## Why Typed Bit2Me?

- **🎯 Precise Types**: literal types for order sides, order types, and statuses; `Decimal` for prices and amounts; a full `TypedDict` per response.
- **✅ Runtime Validation**: every REST response and every WebSocket push is validated against its documented schema by default.
- **⚡ Async First**: async HTTP plus two independent WebSocket surfaces (the Trading Spot socket for order commands and channel subscriptions, and the account-notifications socket), built for concurrent trading workflows.
- **📚 Full Surface**: the complete `v1`/`v2`/`v3` REST surface (trading, wallet, account, earn, and more), not just tickers.

## Installation

```bash
pip install typed-bit2me
```

## How To

- [Fetch Market Data](https://tribulnation.com/typed/bit2me/how-to/fetch-market-data)
- [Listen To Streams](https://tribulnation.com/typed/bit2me/how-to/listen-to-streams)
- [Place & Manage Orders](https://tribulnation.com/typed/bit2me/how-to/place-and-manage-orders)
- [Fetch Account Data](https://tribulnation.com/typed/bit2me/how-to/fetch-account-data)
- [Query & Manage Earn](https://tribulnation.com/typed/bit2me/how-to/manage-earn)
- [Query & Manage Deposits/Withdrawals](https://tribulnation.com/typed/bit2me/how-to/manage-deposits-and-withdrawals)

## Reference

- [Getting Started](https://tribulnation.com/typed/bit2me/getting-started)
- [Async Usage](https://tribulnation.com/typed/bit2me/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/bit2me/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/bit2me/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/bit2me/reference/timestamps)

## Design Philosophy

Typed Bit2Me follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
