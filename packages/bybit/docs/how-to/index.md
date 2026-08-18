# Overview

Task-focused guides for the public market surface. Every example is runnable as written — no
credentials, no setup.

## Included Guides

- [Fetch Candles](fetch-candles.md) - traded, mark, index, and premium index klines
- [Read The Order Book](read-the-order-book.md) - depth snapshots, full depth, and RPI depth
- [List Instruments](list-instruments.md) - trading rules, tick sizes, and risk limits
- [Read Tickers And Trades](read-tickers.md) - price snapshots, the tape, and price bands
- [Paginate Through Results](paginate-through-results.md) - cursor and time-window paging

## Account Data, Streams, And Orders

These guides only cover `client.http.market`. For wallet balances, live order book and wallet
streams, and WS order entry, see [Async Usage](../reference/async-usage.md) and
[API Keys Setup](../api-keys.md) — those surfaces need credentials, which these examples
deliberately don't.

## Running The Examples

Each snippet is a complete program body. To run one, wrap it in `asyncio.run`:

```python
import asyncio
from bybit import Bybit

async def main():
  async with Bybit.new(public=True) as client:
    server_time = await client.http.market.time()
    print(server_time['timeSecond'])

asyncio.run(main())
```

The remaining guides omit the `asyncio.run` scaffolding for brevity.
