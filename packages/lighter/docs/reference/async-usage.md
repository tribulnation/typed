# Async Usage

The Lighter client is async-first and supports two usage styles:

- build a client and call methods directly, for quick one-off scripts
- use `async with`, to close every connection cleanly when you are done

## Quick Usage

`Lighter.new()` resolves credentials and builds the client without connecting to anything.
Connections open on first use:

```python
from typed_lighter import Lighter

client = Lighter.new(public=True)
status = await client.api.system.status()
```

## Context Manager Usage

`async with` on the top-level client is the only lifecycle call you make. It opens nothing
up front: the REST connection pool, the WebSocket connection, the explorer and the deposit
bridge each connect lazily on first use, and on exit the client closes whichever of them
were opened. Every one of them is closed even if closing another fails, or if the task
leaving the block is cancelled.

If another task is still opening the WebSocket connection when the block exits, the exit
doesn't wait for it. That connect closes what it opened and raises `NetworkError`, so no
connection outlives the block. Work that starts after the exit gets a fresh connection.

Exiting does not retire the client. Using it after the block silently opens new
connections (the REST connection pool, or the WebSocket connection with its background
keepalive), and only another exit of the top-level client closes them. Don't use a client
after its block ends; if you do, enter it again with `async with`.

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  books = await client.api.markets.order_books()
  await client.tx.cancel_all_orders({'mode': 'immediate'}, transport='ws')
```

Enter only the top-level client. `client.api`, `client.tx`, `client.streams`,
`client.explorer` and `client.deposit_bridge` share its connections, so they never close
them: `async with client.tx:` (or any of those five) is allowed but does nothing, and a
live stream keeps receiving after such a block ends. `client.signer` and `Scaler` hold no
connection and don't support `async with` at all.

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  async with client.streams.trades(0) as trades:
    async with client.tx:  # does nothing: the WebSocket stays open
      await client.tx.cancel_all_orders({'mode': 'immediate'}, transport='ws')
    async for frame in trades:
      print(frame['trades'])
      break
# the connections close here
```

## Streams

Every subscription can be used two ways. With `async with`, leaving the block unsubscribes:

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  async with client.streams.trades(0) as trades:
    async for frame in trades:
      print(frame['trades'])
```

With `await`, the subscription stays open until you unsubscribe:

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  trades = await client.streams.trades(0)
  async for frame in trades:
    print(frame['trades'])
    break
  await trades.unsubscribe()
```

## Shared Connections

The client's surfaces share their transports:

- `client.api` and `client.tx` (over HTTP) use one REST connection pool.
- `client.streams` and `client.tx` (with `transport='ws'`) use one WebSocket connection:
  subscriptions and transactions are multiplexed over it.
- `client.explorer` and `client.deposit_bridge` have hosts of their own.

Independent calls can run concurrently:

```python
import asyncio

from typed_lighter import Lighter

async with Lighter.new() as client:
  account = client.signer.account_index
  books, orders = await asyncio.gather(
    client.api.markets.order_books(),
    client.api.account.orders.active(account_index=account),
  )
```

Concurrent transactions are safe too. Each API key's nonces are handed out under a
per-key lock held from signing through submission, so transactions on one key reach
Lighter in nonce order; with several keys configured, transactions rotate across them and
run in parallel.

## Guidance

Use `async with` on the top-level client by default: it is the only way to close the
connections deterministically, and a WebSocket connection left open keeps a background
keepalive running. Without it, connections still open on first use and stay open until the
process ends. Plain construction is fine for short scripts and for signing offline, which
opens no connection at all.
