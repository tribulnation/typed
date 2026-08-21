# Typed MEXC

> A fully typed, validated async client for the MEXC spot and futures APIs.

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  candles = await client.spot.market.candles(symbol='BTCUSDT', interval='1m', limit=5)
  stream = await client.futures.streams.market.ticker('BTC_USDT')
  print(candles[-1][4])

  async for ticker in stream:
    print(ticker.get('lastPrice'))
    break
```

## Why Typed MEXC?

- **🎯 Precise Types**: Typed endpoint inputs and responses.
- **✅ Runtime Validation**: Validated responses by default.
- **⚡ Async First**: HTTP and WebSocket subscriptions.
- **📚 Full API Surface**: `client.spot`, `client.futures`, and stream groups for both spot and futures.

## Installation

```bash
pip install typed-mexc
```

## How To

- [API Keys Setup](api-keys.md)
- [Fetch Market Data](how-to/fetch-market-data.md)
- [Place & Manage Orders](how-to/place-and-manage-orders.md)
- [Fetch Balances, Positions & History](how-to/fetch-balances-positions-and-history.md)
- [Manage Deposits & Withdrawals](how-to/manage-deposits-and-withdrawals.md)
- [Listen To Streams](how-to/listen-to-streams.md)

## Reference

- [Async Usage](reference/async-usage.md)
- [Error Handling](reference/error-handling.md)
- [Environment Variables](reference/env-vars.md)
- [Timestamps](reference/timestamps.md)

## Design Philosophy

Typed MEXC follows the principles outlined in [this blog post](https://tribulnation.com/blog/clients).

*Details matter. Developer experience matters.*
