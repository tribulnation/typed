<p align="center">
  <a href="https://tribulnation.com/typed/kraken">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/kraken/media/kraken-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/kraken/media/kraken-light.svg">
      <img alt="Typed Kraken" src="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/kraken/media/kraken-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Kraken Spot API -- REST and WebSocket v2.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-kraken/">
    <img src="https://img.shields.io/pypi/v/typed-kraken.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-kraken/">
    <img src="https://img.shields.io/pypi/pyversions/typed-kraken.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/kraken">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-kraken.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/kraken](https://tribulnation.com/typed/kraken)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/kraken](https://github.com/tribulnation/typed/tree/main/packages/kraken)

---

```python
from typed_kraken import Kraken

async with Kraken.new(public=True) as client:
  ticker = await client.spot.market_data.ticker(pair='XBTUSD')
  print(ticker)
```

## Why Typed Kraken?

- **🎯 Precise Types**: every `client.spot`, `client.streams`, and `client.trading_ws`
  parameter and response is typed, down to `TypedDict`s and `Literal`s for Kraken's own
  field names.
- **✅ Runtime Validation**: REST and WebSocket v2 responses are validated against their
  schema before you see them, not just typed on paper.
- **⚡ Async First**: async REST calls and long-lived WebSocket v2 subscriptions, built for
  concurrent trading workflows.
- **📚 Full Surface**: market data, account, trading, funding, and earn -- every documented
  Kraken Spot endpoint, not just the popular ones.

## Installation

```bash
pip install typed-kraken
```

## How To

- [Fetch Market Data](https://tribulnation.com/typed/kraken/how-to/fetch-market-data)
- [Listen To Streams](https://tribulnation.com/typed/kraken/how-to/listen-to-streams)
- [Place & Manage Orders](https://tribulnation.com/typed/kraken/how-to/place-and-manage-orders)
- [Fetch Account Data](https://tribulnation.com/typed/kraken/how-to/fetch-account-data)
- [Query & Manage Earn Instruments](https://tribulnation.com/typed/kraken/how-to/query-and-manage-earn)
- [Deposits & Withdrawals](https://tribulnation.com/typed/kraken/how-to/deposits-and-withdrawals)

## Reference

- [API Keys Setup](https://tribulnation.com/typed/kraken/api-keys)
- [Async Usage](https://tribulnation.com/typed/kraken/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/kraken/reference/error-handling)
- [Environment Variables](https://tribulnation.com/typed/kraken/reference/env-vars)
- [Timestamps](https://tribulnation.com/typed/kraken/reference/timestamps)

## Design Philosophy

Typed Kraken follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT -- see [LICENSE](LICENSE).
