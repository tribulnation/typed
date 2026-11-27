# Paginate Through Results

Five calls page through their results, and each has a `_paged` variant that walks every page
for you:

| Method | Walks by | Order |
| --- | --- | --- |
| `client.market.candles_paged(...)` | moving `end` back to the oldest candle of each page | newest first |
| `client.market.liquidity_events_paged(...)` | page number, up to 15 events a page | newest first |
| `client.market.token.created_paged(...)` | Gate's `next_cursor` | newest first |
| `client.market.token.ranking_paged(...)` | Gate's `next_cursor` | ranking order |
| `client.trade.history_paged(...)` | page number, up to 100 orders a page | as Gate returns them |

They take the same arguments as the single-page call, minus the page index or cursor.

## Every Row At Once

Awaiting a paged call fetches every page and returns one flat list:

```python
from datetime import datetime, timezone
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  candles = await client.market.candles_paged(
    chain_id=1,
    token_address='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
    period=3600,
    start=datetime(2026, 10, 12, tzinfo=timezone.utc),
    end=datetime(2026, 10, 17, tzinfo=timezone.utc),
    limit=300,
  )
  print(len(candles), candles[0]['ts'], candles[-1]['ts'])
```

Without `start`, `candles_paged` keeps walking back until Gate has nothing older; it keeps
the latest 1440 candles per token and period.

Give `candles_paged` a `limit` of at least 2. Gate's `end` bound is inclusive, so each page
after the first opens with the candle the previous page ended on. A one-candle page holds
nothing else, so with `limit=1` the walk cannot move on and raises `LogicError`.

## One Page At A Time

Iterate to handle pages as they arrive, and stop whenever you have enough:

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  async for tokens in client.market.token.ranking_paged(
    chain_id={'in': ['1', '501']},
    sort=[{'field': 'trend_info.volume_24h', 'order': 'desc'}],
    limit=10,
  ):
    for token in tokens:
      print(token['chain'], token['symbol'], token['liquidity'])
    break  # the top 10 is enough
```

Gate publishes no maximum `limit` for rankings. As of October 2026, `limit=500` fails with
code `41002`, raised as `ApiError`.

## Staying Under The Rate Limit

Each page is one request, and Gate's free tier allows about one request per second. `via`
routes every page fetch through a function of yours, such as a delay:

```python
import asyncio
from datetime import datetime, timezone
from typing import Awaitable, Callable, TypeVar
from typed_gate_dex import GateDex

T = TypeVar('T')


async def throttled(fetch: Callable[[], Awaitable[T]]) -> T:
  """Wait a second before each page."""
  await asyncio.sleep(1)
  return await fetch()


async with GateDex.new() as client:
  walk = client.market.token.created_paged(
    start=datetime(2026, 10, 26, tzinfo=timezone.utc),
    end=datetime(2026, 10, 27, tzinfo=timezone.utc),
    chain_id='1',
    limit='100',
  )
  tokens = await walk.via(throttled)
```

The same hook fits a retry policy: a failed page can be fetched again without restarting
the walk.

## Resuming A Walk

`pages()` exposes each page's state, so a long walk can be checkpointed and resumed later:

```python
from typed_gate_dex import GateDex

async with GateDex.new() as client:
  walk = client.market.liquidity_events_paged(
    chain_id=1, token_address='0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'
  )
  checkpoint = None
  async for page in walk.pages():
    print(len(page.rows))
    checkpoint = page.next  # the next page number; None after the last page
    break
  if checkpoint is not None:
    async for events in walk.resume(checkpoint):  # carries on from the next page
      print(len(events))
      break
```

Liquidity events come newest first, so on an active token new events push rows onto later
pages while a walk is in progress and the walk can return the same event twice; deduplicate
on `(event['txn_hash'], event['log_index'])`.

## Order History

`client.trade.history_paged(user_wallet=[...])` walks a wallet's swap orders. As of October
2026, Gate answers every history request with code `20009` (`JSON parse error`), raised as
`BadRequest`.
