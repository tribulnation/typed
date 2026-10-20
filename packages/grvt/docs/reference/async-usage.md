# Async Usage

Typed GRVT is async-first and supports two usage styles:

- construct a client and call methods directly, for quick one-off requests
- use `async with` to own the client's connections and close them cleanly

## Quick Usage

```python
from typed_grvt import Grvt

client = Grvt.new(public=True)
book = await client.market.orderbook('BTC_USDT_Perp', depth=10)
print(book['bids'][0])
```

Connections open lazily on first use. Without `async with`, nothing closes them for you.

## Context Manager Usage

```python
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  summary = await client.trading.account_summary()
  positions = await client.trading.positions()
  print(summary['total_equity'], len(positions))
```

Entering the top-level client is the only thing you do. Every surface (`market`,
`market_streams`, `trading`, `trading_streams`, `edge`) and every underlying connection,
HTTP or WebSocket, is entered with it and opens lazily on first use. You never enter a
sub-surface separately. Leaving the block closes everything that was opened.

## Streams

Subscribe with `async with` to unsubscribe automatically when the block ends:

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  async with client.market_streams.ticker('BTC_USDT_Perp', rate=500) as stream:
    async for ticker in stream:
      print(ticker.get('mark_price'))
      break
```

Or `await` the subscription and unsubscribe yourself:

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  stream = await client.market_streams.ticker('BTC_USDT_Perp', rate=500)
  async for ticker in stream:
    print(ticker.get('mark_price'))
    break
  await stream.unsubscribe()
```

## One Client, Several Surfaces

GRVT has three hosts: market data, trading, and edge (deposits, bridge, referrals). One
`Grvt` client holds a connection pool per host plus one WebSocket per gateway. Market data
and trading each have one socket shared by RPC calls (`transport='ws'`) and streams.

Trading and edge calls share one session, opened on the first authenticated call (with the
API key, or with a wallet signature when there is none). Market data is public and never
sends it. The session is refreshed before it expires and, if GRVT rejects it, renewed and the
call retried once. Concurrent calls share one login.

The trading WebSocket keeps the session it connected with. When GRVT rejects that session
(code `1000`) on a call or subscription over it, the client closes the connection, reconnects
with a renewed session and retries once. Closing the old connection ends every private stream
still live on it with `NetworkError`: subscribe again to resume.

A non-JSON `401` or `403`, such as a Cloudflare challenge page in front of a GRVT host, is not
GRVT rejecting the session: it raises `ApiError` (`Blocked by ...`) and is not retried.

## Guidance

1. Use `async with` by default, and always for streams or more than one call.
2. Run independent calls concurrently with `asyncio.gather`: one client is safe to share
   across tasks.
3. To reuse one client across event loops (for example several `asyncio.run` calls), enter
   it with `async with` inside each loop. Leaving the block releases connections bound to
   the old loop; a client used without `async with` in a second loop fails with
   `RuntimeError`.
