<p align="center">
  <a href="https://tribulnation.com/typed/bybit">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/bybit/media/bybit-dark.svg">
      <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/bybit/media/bybit-light.svg">
      <img alt="Typed Bybit" src="https://raw.githubusercontent.com/tribulnation/typed/refs/heads/main/packages/bybit/media/bybit-light.svg" width="520">
    </picture>
  </a>
</p>

<p align="center">
  <em>A fully typed, validated async client for the Bybit v5 API.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/typed-bybit/">
    <img src="https://img.shields.io/pypi/v/typed-bybit.svg" alt="PyPI version">
  </a>
  <a href="https://pypi.org/project/typed-bybit/">
    <img src="https://img.shields.io/pypi/pyversions/typed-bybit.svg" alt="Python versions">
  </a>
  <a href="https://tribulnation.com/typed/bybit">
    <img src="https://img.shields.io/badge/docs-live-black" alt="Docs">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/pypi/l/typed-bybit.svg" alt="License">
  </a>
</p>

---

- **Documentation**: [https://tribulnation.com/typed/bybit](https://tribulnation.com/typed/bybit)
- **Source Code**: [https://github.com/tribulnation/typed/tree/main/packages/bybit](https://github.com/tribulnation/typed/tree/main/packages/bybit)

---

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  ticker = await client.http.market.tickers(category='spot', symbol='BTCUSDT')
  print(ticker['list'][0]['lastPrice'])
```

## Why Typed Bybit?

- **🎯 Precise Types**: Typed inputs and responses across REST and WebSocket, discriminated by product category.
- **✅ Runtime Validation**: Responses and pushed stream messages validated by default.
- **⚡ Async First**: One shared HTTP pool and eight lazily-opened WebSocket connections, built for concurrent workflows.
- **📚 Full Surface**: Every documented v5 Market endpoint, wallet balances, and live public/private/order-entry streams.

## Installation

```bash
pip install typed-bybit
```

## How To

- [Fetch Candles](https://tribulnation.com/typed/bybit/how-to/fetch-candles)
- [Read The Order Book](https://tribulnation.com/typed/bybit/how-to/read-the-order-book)
- [List Instruments](https://tribulnation.com/typed/bybit/how-to/list-instruments)
- [Read Tickers And Trades](https://tribulnation.com/typed/bybit/how-to/read-tickers)
- [Paginate Through Results](https://tribulnation.com/typed/bybit/how-to/paginate-through-results)

## Reference

- [API Keys Setup](https://tribulnation.com/typed/bybit/api-keys)
- [Async Usage](https://tribulnation.com/typed/bybit/reference/async-usage)
- [Error Handling](https://tribulnation.com/typed/bybit/reference/error-handling)
- [Configuration](https://tribulnation.com/typed/bybit/reference/configuration)
- [Timestamps](https://tribulnation.com/typed/bybit/reference/timestamps)

## Design Philosophy

Typed Bybit follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*

## License

MIT — see [LICENSE](LICENSE).
