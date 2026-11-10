# Async Usage

Typed gTrade is async-first and supports two usage styles:

- construct a client and call methods directly, for quick one-off requests
- use `async with`, for explicit lifecycle management

## Quick Usage

```python
from typed_gtrade import GTrade

client = GTrade.new(public=True)
prices = await client.trading.markets.prices()
```

Every transport opens lazily on first use, so plain construction is enough for a short
script. Nothing closes the connections it opened, though; prefer `async with` for anything
longer.

## Context Manager Usage

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  markets = await client.trading.markets.list()
  book = await client.trading.markets.book('BTC/USD')
```

Entering the root client is the only thing you do. Every surface underneath (`trading`,
`backend`, `backend_global`, `pricing`, and each one's WebSocket) opens lazily the first
time it is used, and leaving the block closes everything that was opened. You never enter a
sub-client yourself.

## Streams

Each stream method supports two styles.

With `async with`, leaving the block unsubscribes:

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  async with client.trading.streams.trades('BTC/USD') as trades:
    async for frame in trades:
      print(frame['data'])
```

With `await`, you unsubscribe yourself:

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  trades = await client.trading.streams.trades('BTC/USD')
  async for frame in trades:
    print(frame['data'])
    break
  await trades.unsubscribe()
```

Subscriptions on the same feed share one connection: the Trading API, the per-chain backend
and pricing each use a single WebSocket per client.

## Several Surfaces at Once

The four surfaces are independent services, so their calls run concurrently:

```python
import asyncio
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  prices, trading_variables, charts = await asyncio.gather(
    client.trading.markets.prices(),
    client.backend.trading_variables.by_keys(['pairs']),
    client.pricing.snapshots.charts(),
  )
```

One client serves one chain. To work on two chains, build two clients and enter both:

```python
from typed_gtrade import GTrade

async with GTrade.new(chain='arbitrum', public=True) as arbitrum, GTrade.new(chain='base', public=True) as base:
  arbitrum_trades = await arbitrum.backend.trades.open()
  base_trades = await base.backend.trades.open()
```

## Guidance

Use direct construction for a quick read. Use `async with` by default: when making more
than one call, opening streams, or wanting predictable cleanup.
