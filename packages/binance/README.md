# Typed Binance

> A fully typed, validated async client for the Binance API.

```python
from binance import Binance

async with Binance.new(public=True) as client:
  price = await client.spot.market.ticker_price(symbol='BTCUSDT')
  print(price)
```

## Why Typed Binance?

- **Typed everything**: every parameter and response is a precise Python type, not `dict[str, Any]`.
- **Validated by default**: responses are checked against their schema at runtime.
- **Async first**: built on `asyncio`, with async iterators for paginated endpoints and streaming subscriptions.
- **One client, every product**: spot, USD-M futures, COIN-M futures, options, and portfolio margin all live on one `Binance` instance, alongside their WebSocket market-data streams and WS APIs.

## Installation

```bash
pip install typed-binance
```

## Documentation

- [API Keys Setup](docs/api-keys.md)
- [How To](docs/how-to/index.md)
- [Reference](docs/reference/index.md)
