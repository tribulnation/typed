# Async Usage

The client is async-first and supports two usage styles:

- construct it and call methods directly, for a quick one-off request
- use `async with`, for explicit lifecycle management

## Quick Usage

Both transports (one HTTP connection pool, one WebSocket) open lazily on first use, so a
plain client works without a block:

```python
from typed_margin_trade import MarginTrade

client = MarginTrade.new(public=True)
mids = await client.info.all_mids()
```

Without `async with`, nothing closes the connection pool for you when you are done.

## Context Manager Usage

`async with` on the root client is the only lifecycle step you take. It opens nothing up
front; each transport connects when first used, and both close when the block exits.
Every surface underneath (`info`, `exchange`, `user`, `solana`, `public`, `coingecko`,
`streams`) shares the root's transports and enters lazily as it is first used, so you never
enter a surface separately.

```python
import os
from typed_margin_trade import MarginTrade, Wallet

wallet = Wallet.parse(os.environ['MARGIN_TRADE_TESTNET_PRIVATE_KEY'])

async with MarginTrade.new(wallet, mainnet=False) as client:
  state = await client.info.clearinghouse_state(user=wallet.address)
  profile = await client.user.get_user()
  agents = await client.exchange.get_agents()
```

## Streams

Every subscription shares the one WebSocket connection, opened by the first subscribe.
There are two ways to hold a subscription.

`async with` unsubscribes automatically when the block exits:

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  async with client.streams.l2_book('BTC') as stream:
    async for book in stream:
      print(book['time'])
      break
```

`await` returns the subscription, and you unsubscribe explicitly:

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  sub = await client.streams.l2_book('BTC')
  print(sub.reply)  # the subscribe acknowledgement
  async for book in sub:
    print(book['time'])
    break
  await sub.unsubscribe()
```

Subscriptions to the same channel for different markets (`l2_book('BTC')` and
`l2_book('ETH')`) run side by side on the one connection, and each receives only its own
market's pushes.

## Concurrent Requests

Calls on one client can run concurrently over the shared pool:

```python
import asyncio
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  btc, eth, mids = await asyncio.gather(
    client.info.l2_book('BTC'),
    client.info.l2_book('ETH'),
    client.info.all_mids(),
  )
```

## Guidance

Use direct construction for a quick read. Use `async with` by default when making more than
one call, opening streams, or wanting predictable cleanup.
