# Typed RISEx

<p align="center">
  <em>A fully typed, validated async client for the RISEx API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-risex/">
    <img src="https://img.shields.io/pypi/v/typed-risex.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-risex/">
    <img src="https://img.shields.io/pypi/pyversions/typed-risex.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/risex">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-risex.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/risex](https://tribulnation.com/typed/risex)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/risex](https://github.com/tribulnation/typed/tree/main/packages/risex)

---

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  markets = await client.markets.all()
  book = await client.markets.orderbook(market_id=1, limit=5)
  print(markets['markets'][0]['config']['name'], book['bids'][0]['price'])
```

## Why Typed RISEx?

- **🎯 Precise Types**: Typed requests and responses for every REST endpoint and WebSocket channel, with order bodies typed as limit/market unions, not `dict`/`Any`.
- **✅ Runtime Validation**: Responses validated by default, with prices and amounts as `Decimal` (or `''` where RISEx sends no value, and raw 10^18-scaled `int`s where it returns on-chain values; a few affiliate, leaderboard and points amounts with no observed value stay `str`), and timestamps as `datetime` with a few exceptions (see [Timestamps](https://tribulnation.com/typed/risex/reference/timestamps)).
- **⚡ Async First**: Async HTTP and a single multiplexed WebSocket feed, with EIP-712 permits, nonces and JWT sessions signed for you.
- **📚 Full Surface**: The full trading, account and market-data API: markets, orders, TP/SL, positions and margin, portfolio, signers and sessions, points, competition and leaderboard reads, and stats.

## Installation

```bash
pip install typed-risex
```

## Setup

RISEx has no API keys: you trade with an EVM account key plus a registered signer (session) key. See [Authenticated Setup](https://tribulnation.com/typed/risex/authenticated-setup) to create both on testnet, claim test USDC, and register the signer.

## How To

- [Fetch Market Data](https://tribulnation.com/typed/risex/how-to/fetch-market-data)
- [Fetch Account Data](https://tribulnation.com/typed/risex/how-to/fetch-account-data)
- [Place & Manage Orders](https://tribulnation.com/typed/risex/how-to/place-and-manage-orders)
- [Manage Leverage & Margin](https://tribulnation.com/typed/risex/how-to/manage-leverage-and-margin)
- [Paginate Through Results](https://tribulnation.com/typed/risex/how-to/paginate-through-results)
- [Listen To Live Streams](https://tribulnation.com/typed/risex/how-to/listen-to-live-streams)

## Reference

- [Authenticated Setup](https://tribulnation.com/typed/risex/authenticated-setup)
- [Async Usage](https://tribulnation.com/typed/risex/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/risex/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/risex/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/risex/reference/timestamps)

## Design Philosophy

Typed RISEx follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
