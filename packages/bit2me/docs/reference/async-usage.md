# Async Usage

Bit2Me clients are async-first and support two usage styles:

- construct a client and call methods directly for quick one-off requests
- use `async with` when you want explicit lifecycle management

## Quick Usage

For short request-response flows against the REST surface, plain construction is fine — the
underlying HTTP transport opens lazily on first use.

```python
from typed_bit2me import Bit2Me

client = Bit2Me.new(public=True)
book = await client.v2.trading.order_book(symbol='BTC/EUR')
print(book.get('bids', [])[:1])
```

## Context Manager Usage

Use `async with` to open the client up front and close it cleanly at the end of the block.

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()
  orders = await client.v1.trading.orders.list(limit=5)
```

**`Bit2Me`'s own `async with` only opens `client.http`.** `client.v1`, `client.v2`, and
`client.v3` all share that one HTTP transport, so nothing further is needed for the REST
surface. This is the one place Bit2Me departs from every other client in this catalog: the
top-level `async with` does **not** also open `client.trading_ws` or `client.crypto_ws` — each
WebSocket surface connects only when you separately enter it with its own `async with`.

## WebSocket Surfaces

`client.trading_ws` (the Trading Spot socket) and `client.crypto_ws` (account notifications)
are two independent connections, and each needs its own `async with` before use:

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  async with client.trading_ws as trading:
    ...  # subscribe to channels or send order commands here
```

For `client.trading_ws`, entering it is also what authenticates the connection when the
client holds credentials — there's no separate login step. `client.crypto_ws` needs an
explicit `authenticate(payload={'token': ...})` call after entering (see Getting Started's
WebSocket section and [Listen To Streams](../how-to/listen-to-streams.md)).

## Streams

`client.trading_ws`'s channel subscriptions (`order_book`, `public_trades`, `my_orders`,
`my_trades`, `my_balance`, `my_working_capital`) return a subscription manager, not a stream
directly. `order_book`/`public_trades` are public; the rest need an authenticated connection
via `authed_subscribe` under the hood. Both usage variants work:

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new(public=True) as client:
  async with client.trading_ws as trading:
    async with trading.order_book(symbol='BTC/EUR') as stream:
      async for update in stream:
        print(update['bids'][:1], update['asks'][:1])
    # auto-unsubscribed on block exit
```

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new(public=True) as client:
  async with client.trading_ws as trading:
    stream = await trading.order_book(symbol='BTC/EUR')
    async for update in stream:
      print(update['bids'][:1])
      break
    await stream.unsubscribe()
```

`client.crypto_ws` has no subscribe/unsubscribe protocol at all: after `authenticate(...)`,
every notification your account is entitled to arrives unprompted on `notifications()`, so
there's no separate stream manager to unsubscribe from.

## Guidance

Use direct construction for quick reads. Use `async with` by default when doing more than one
call, and always wrap `client.trading_ws`/`client.crypto_ws` in their own `async with` when
you need either WebSocket surface — the top-level `async with Bit2Me.new()` does not cover
them.
