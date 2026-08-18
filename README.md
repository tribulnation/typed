# Typed Clients

Async, typed, validated Python clients for every crypto venue we trade on. One namespace. Every exchange.

```python
from binance import Binance

async with Binance.new(public=True) as client:
  price = await client.spot.market.ticker_price(symbol='BTCUSDT')
  print(price)
```

## Why typed?

- **🎯 Precise Types**: Typed endpoint inputs and responses, not `dict`/`Any`.
- **✅ Runtime Validation**: Responses validated by default, not just typed on paper.
- **⚡ Async First**: Async HTTP and streaming, built for concurrent workflows.
- **📚 Full Surface**: Every documented endpoint, not just the popular ones.

## Packages

| package | description |
| --- | --- |
| [`typed-core`](packages/core) | shared types & utilities every client core builds on |
| [`typed-binance`](packages/binance) | spot, USD-M futures, COIN-M futures, options, and portfolio margin |

More venues are on the way — see the [full catalog](https://tribulnation.com/typed).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md): most of the source code is generated from an internal spec. So, open issues not PRs please! If you want to collaborate further, please reach out to us at marcel@tribulnation.com :)

## License

MIT — see [LICENSE](LICENSE).
