# Typed Binance

> A fully typed, validated async client for the Binance API.

```python
from binance import Binance

async with Binance.new(public=True) as client:
  price = await client.spot.market.ticker_price(symbol='BTCUSDT')
  print(price)
```

## Why Typed Binance?

- **🎯 Precise Types**: every spot, USD-M futures, COIN-M futures, options, and portfolio margin parameter and response is a precise Python type, not `dict`/`Any`.
- **✅ Runtime Validation**: every response is validated against its schema by default, not just typed on paper.
- **⚡ Async First**: async HTTP requests and WebSocket market-data streams, built for concurrent workflows across every product line.
- **📚 Full Surface**: every documented spot, futures, options, and portfolio margin endpoint, not just the popular ones.

## Installation

```bash
pip install typed-binance
```

## Documentation

- [API Keys Setup](api-keys.md)
- [How To](how-to/index.md)
- [Reference](reference/index.md)
