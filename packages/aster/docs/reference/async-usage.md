# Async Usage

Typed Aster is async-first and supports two usage styles:

- construct a client and call methods directly
- use `async with` for explicit lifecycle management

## Quick Usage

Plain construction is fine for short scripts. Connections open lazily on first use:

```python
from typed_aster import Aster

client = Aster.new(public=True)
print(await client.spot.market.time())
```

## Context Manager Usage

Use `async with` for anything longer-lived. Entering `Aster` is the only thing you do:
`futures`, `spot`, `prediction` and `chain`, and each one's HTTP and WebSocket connections,
open lazily the first time you use them, and all of them close when the block exits. You never
enter a sub-client yourself.

```python
from typed_aster import Aster

async with Aster.new() as client:
  balances = await client.futures.account.balance()
  spot = await client.spot.account.info()
```

## Streams

Each stream supports two styles. With `async with`, it unsubscribes when the block exits:

```python
from typed_aster import Aster

async with Aster.new(public=True) as client:
  async with client.futures.streams.mark_price('btcusdt') as stream:
    async for update in stream:
      print(update['p'])
```

Or await it and unsubscribe yourself:

```python
from typed_aster import Aster

async with Aster.new(public=True) as client:
  stream = await client.futures.streams.mark_price('btcusdt')
  async for update in stream:
    print(update['p'])
    break
  await stream.unsubscribe()
```

All market streams of one surface share one WebSocket connection. Each user stream uses its
own connection, identified by its listenKey.

## Multi-Surface Client

`futures`, `spot`, `prediction` and `chain` share one set of credentials but have their own
connections, so you can use them concurrently:

```python
import asyncio

from typed_aster import Aster

async with Aster.new(public=True) as client:
  futures_book, spot_book = await asyncio.gather(
    client.futures.market.depth('BTCUSDT'),
    client.spot.market.depth('BTCUSDT'),
  )
```

## Guidance

Use direct construction for one-off reads. Use `async with` by default when making several
calls, opening streams, or wanting predictable cleanup.
