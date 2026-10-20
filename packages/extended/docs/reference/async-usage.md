# Async Usage

Every call is a coroutine. A client can be used directly, or entered with `async with` so its
connections are closed for you.

## Quick Usage

```python
from typed_extended import Extended

client = Extended.new(public=True)
markets = await client.info.markets()
```

This is fine for scripts and notebooks. The HTTP connection pool stays open until the process
exits.

## Context Manager Usage

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  markets = await client.info.markets()
  book = await client.info.orderbook('BTC-USD')
# connection pool and every open stream closed here
```

Entering the client opens nothing: the HTTP pool connects on the first request, and each
stream connects when you subscribe. Leaving it closes the pool and any stream still open.

## Streams

Each subscription is its own WebSocket connection. Enter it to unsubscribe automatically:

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  async with client.streams.trades('BTC-USD') as stream:
    async for message in stream:
      print(message['data'])
  # unsubscribed (connection closed) here
```

Or await it and unsubscribe yourself:

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  stream = await client.streams.trades('BTC-USD')
  async for message in stream:
    print(message['data'])
    break
  await stream.unsubscribe()
```

## Composite Client

`Extended` groups its surfaces as attributes: `info`, `account`, `orders`, `funds`,
`portfolio`, `streams`, `vault`, `interest`, `points`, `referrals` and `builder`. They share
the root's HTTP pool and credentials. Entering the root client is the only thing you do;
every sub-surface is ready as soon as you first use it, and you never enter one separately.

## Guidance

- Prefer one `Extended` client per process and network, shared across tasks.
- Run independent requests concurrently with `asyncio.gather`:

```python
import asyncio
from typed_extended import Extended

async with Extended.new(public=True) as client:
  btc, eth = await asyncio.gather(
    client.info.market_stats('BTC-USD'),
    client.info.market_stats('ETH-USD'),
  )
```

- Pass `validate=False` to any call (or to `Extended.new`) to skip response validation on a
  hot path.
