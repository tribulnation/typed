<p align="center">
  <a href="https://tribulnation.com/typed/evedex">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://tribulnation.com/media/lockups/evedex-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://tribulnation.com/media/lockups/evedex-light.svg">
      <img alt="Typed EVEDEX" src="https://tribulnation.com/media/lockups/evedex-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the EVEDEX API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-evedex/">
    <img src="https://img.shields.io/pypi/v/typed-evedex.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-evedex/">
    <img src="https://img.shields.io/pypi/pyversions/typed-evedex.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/evedex">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-evedex.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/evedex](https://tribulnation.com/typed/evedex)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/evedex](https://github.com/tribulnation/typed/tree/main/packages/evedex)

---

```python
from typed_evedex import Evedex

async with Evedex.new(public=True) as client:
  book = await client.exchange.market.order_book(instrument='BTCUSD')
  print(book['bids'][0], book['asks'][0])
```

## Why Typed EVEDEX?

- **🎯 Precise Types**: Typed requests and responses for every EVEDEX perpetual endpoint, with prices and sizes as `Decimal` and times as `datetime`, not `dict`/`Any`.
- **✅ Runtime Validation**: Every HTTP response and WebSocket publication is validated by default, not just typed on paper.
- **⚡ Async First**: Async HTTP for the Exchange, Auth and market-data services and async Centrifugo streams, sharing one client.
- **📚 Full Surface**: Market data, account, orders (single and batch), positions, TP/SL, transfers, sub-accounts, API keys and every public and private channel, with EIP-712 signing built in.

## Installation

```bash
pip install typed-evedex
```

## Getting Started

Public market data needs no credentials: build the client with `public=True`, as above.
Reading your account needs an API key or your wallet's private key; trading needs the
private key, which signs every order. See [Authenticated Setup](https://tribulnation.com/typed/evedex/authenticated-setup).

```python
from typed_evedex import Evedex

async with Evedex.new() as client:  # reads EVEDEX_PRIVATE_KEY / EVEDEX_API_KEY
  balance = await client.exchange.account.available_balance()
  print(balance['availableBalance'])
```

Pass `env='demo'` to use the EVEDEX demo environment (`evedex.io`) instead of production.

## How To

- [Fetch Market Data](https://tribulnation.com/typed/evedex/how-to/fetch-market-data)
- [Fetch Account Data](https://tribulnation.com/typed/evedex/how-to/fetch-account-data)
- [Place & Manage Orders](https://tribulnation.com/typed/evedex/how-to/place-and-manage-orders)
- [Manage Positions & TP/SL](https://tribulnation.com/typed/evedex/how-to/manage-positions)
- [Listen To Live Streams](https://tribulnation.com/typed/evedex/how-to/listen-to-live-streams)
- [Paginate Through Results](https://tribulnation.com/typed/evedex/how-to/paginate-through-results)

## Reference

- [Authenticated Setup](https://tribulnation.com/typed/evedex/authenticated-setup)
- [Async Usage](https://tribulnation.com/typed/evedex/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/evedex/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/evedex/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/evedex/reference/timestamps)

## License

MIT — see [LICENSE](LICENSE).
