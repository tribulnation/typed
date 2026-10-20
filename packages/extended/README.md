# Typed Extended

<p align="center">
  <em>A fully typed, validated async client for the Extended API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-extended/">
    <img src="https://img.shields.io/pypi/v/typed-extended.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-extended/">
    <img src="https://img.shields.io/pypi/pyversions/typed-extended.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/extended">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-extended.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/extended](https://tribulnation.com/typed/extended)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/extended](https://github.com/tribulnation/typed/tree/main/packages/extended)

---

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  stats = await client.info.market_stats('BTC-USD')
  print(stats['lastPrice'], stats['markPrice'], stats['fundingRate'])
```

## Why Typed Extended?

- **🎯 Precise Types**: Typed inputs and responses for every REST call and WebSocket stream, including the order request union (limit, market, conditional, TP/SL).
- **✅ Runtime Validation**: Responses and stream messages validated by default, with prices and sizes as exact `Decimal` and timestamps as `datetime`.
- **⚡ Async First**: Async HTTP and WebSocket streams, with Stark order, transfer and withdrawal signing done for you.
- **📚 Full Surface**: Market data, account, orders, transfers and withdrawals, portfolio analytics, vault, interest, points, referrals and builder endpoints.

## Installation

```bash
pip install typed-extended
```

Signing runs in pure Python out of the box. For roughly 10x faster signatures, install the
optional native backend:

```bash
pip install "typed-extended[fast]"
```

## How To

- [Fetch Market Data](https://tribulnation.com/typed/extended/how-to/fetch-market-data)
- [Listen To Live Streams](https://tribulnation.com/typed/extended/how-to/listen-to-live-streams)
- [Place & Manage Orders](https://tribulnation.com/typed/extended/how-to/place-and-manage-orders)
- [Fetch Account Data](https://tribulnation.com/typed/extended/how-to/fetch-account-data)
- [Paginate Through Results](https://tribulnation.com/typed/extended/how-to/paginate-through-results)
- [Transfer & Withdraw](https://tribulnation.com/typed/extended/how-to/transfer-and-withdraw)

## Reference

- [Authenticated Setup](https://tribulnation.com/typed/extended/authenticated-setup)
- [Async Usage](https://tribulnation.com/typed/extended/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/extended/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/extended/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/extended/reference/timestamps)

## Design Philosophy

Typed Extended follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
