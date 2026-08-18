# typed

Async, typed, response-validated Python clients for the crypto venues we trade on — one
package per venue, each independently versioned and published to PyPI.

```python
from binance import Binance

async with Binance.new(public=True) as client:
  price = await client.spot.market.ticker_price(symbol='BTCUSDT')
  print(price)
```

## Why typed?

- **Precise types** — every parameter and response is a real Python type, not `dict`/`Any`.
- **Validated by default** — every response is checked against its schema at runtime, not
  just typed on paper.
- **Async first** — built for concurrent HTTP and WebSocket workflows.
- **Explicit about auth** — public and authenticated surfaces are distinct in the API,
  never gated behind an implicit flag.

## Packages

| package | description |
| --- | --- |
| [`typed-core`](packages/core) | shared types & utilities every client core builds on |
| [`typed-binance`](packages/binance) | spot, USD-M futures, COIN-M futures, options, and portfolio margin |

More venues are on the way — see the [full catalog](https://tribulnation.com/typed).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md): most of a client's source is generated from spec,
so a bug in generated code is an issue, not a PR — hand-written surfaces (`core/`, docs,
this README) take PRs directly.

## License

MIT — see [LICENSE](LICENSE).
