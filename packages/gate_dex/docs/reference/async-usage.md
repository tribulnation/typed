# Async Usage

Every call is a coroutine. A client can be used directly, or entered with `async with` so its
connections are closed for you.

## Quick Usage

```python
from typed_gate_dex import GateDex

client = GateDex.new()
chains = await client.trade.chains()
```

This is fine for scripts and notebooks. The HTTP connection pool opens on the first request
and stays open until the process exits.

## Context Manager Usage

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  chains = await client.trade.chains()
  price = await client.market.price(
    chain_id=1, token_address='0xdac17f958d2ee523a2206206994597c13d831ec7'
  )
# connection pool closed here
```

Entering the client opens nothing: the pool connects on the first request. Leaving it closes
the pool.

## Composite Client

`GateDex` groups its calls as attributes: `trade` (swaps) and `market` (market data), with
`market.token` for token data. They all share the root's one HTTP pool and credentials.
Entering the root client is the only thing you do; every sub-surface is ready as soon as you
first use it, and you never enter one separately.

Gate DEX has no streaming API, so there are no subscriptions to manage.

## Guidance

- Prefer one `GateDex` client per API key, shared across tasks.
- Run independent requests concurrently with `asyncio.gather`, keeping Gate's rate limit in
  mind: its free tier allows about one request per second per key, and going faster raises
  `RateLimited`.

```python
import asyncio
from typed_gate_dex import GateDex

usdt = '0xdac17f958d2ee523a2206206994597c13d831ec7'
weth = '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'

async with GateDex.new() as client:
  usdt_price, weth_price = await asyncio.gather(
    client.market.price(chain_id=1, token_address=usdt),
    client.market.price(chain_id=1, token_address=weth),
  )
```

- Pass `validate=False` to any call (or to `GateDex.new`) to skip response validation on a
  hot path.
