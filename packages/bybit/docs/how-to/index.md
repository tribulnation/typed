# Overview

Task-focused guides against the real client surface. Public guides need no credentials;
authenticated ones need `BYBIT_API_KEY`/`BYBIT_API_SECRET` — see
[API Keys Setup](../api-keys.md).

## Market Data (Public)

- [Fetch Candles](fetch-candles.md) - traded, mark, index, and premium index klines
- [Read The Order Book](read-the-order-book.md) - depth snapshots, full depth, and RPI depth
- [List Instruments](list-instruments.md) - trading rules, tick sizes, and risk limits
- [Read Tickers And Trades](read-tickers.md) - price snapshots, the tape, and price bands
- [Listen To Streams](listen-to-streams.md) - public order book/ticker/trade channels, and
  the authenticated `private`/`trade` connections

## Trading And Account (Authenticated)

- [Place & Manage Orders](place-and-manage-orders.md) - create, amend, cancel, and list orders
- [Fetch Account Data](fetch-account-data.md) - wallet balance, positions, and trade history
- [Manage Deposits & Withdrawals](manage-deposits-withdrawals.md) - deposit addresses,
  records, and submitting withdrawals
- [Manage Earn Instruments](manage-earn-instruments.md) - list, subscribe to, and redeem
  fixed-term savings products

## Cross-Cutting

- [Paginate Through Results](paginate-through-results.md) - cursor and time-window paging,
  across market data, orders, positions, and transfers

## Running The Examples

Each snippet is a complete program body. To run one, wrap it in `asyncio.run`:

```python
import asyncio
from typed_bybit import Bybit

async def main():
  async with Bybit.new(public=True) as client:
    server_time = await client.market.time()
    print(server_time['timeSecond'])

asyncio.run(main())
```

The remaining guides omit the `asyncio.run` scaffolding for brevity.
