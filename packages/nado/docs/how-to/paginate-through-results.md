# Paginate Through Results

History endpoints return one page per call, newest first. Each has a `_paged` twin that
walks every page for you:

| Method | Walks |
| --- | --- |
| `archive.candlesticks_paged`, `archive.edge_candlesticks_paged` | candles, back in time |
| `archive.matches_paged`, `archive.matches_and_liquidations_paged` | fills |
| `archive.orders_paged` | historical orders |
| `archive.positions_paged` | open and closed positions |
| `archive.funding_rate_history_paged` | funding rates |
| `archive.nlp_snapshots_paged` | NLP vault snapshots |
| `archive.subaccounts_paged`, `archive.isolated_subaccounts_paged`, `archive.linked_signers_paged` | listings |
| `archive.products_paged` | product snapshots |
| `archive_v2.trades_paged` | public trades by trade id |
| `trigger.list_trigger_orders_paged` | your trigger orders (signed) |

## Everything At Once

Awaiting a `_paged` method fetches every page and returns one flat list:

```python
from datetime import datetime, timezone
from typed_nado import Nado
from typed_nado.core import subaccount_bytes32

me = subaccount_bytes32('0xYourWalletAddress', 'default')

async with Nado.new(public=True) as client:
  fills = await client.archive.matches_paged([me], product_ids=[2], limit=500)
  print(len(fills))

  since_june = await client.archive.orders_paged(
    subaccounts=[me], max_time=datetime(2026, 6, 30, tzinfo=timezone.utc)
  )
```

`max_time` starts the walk at that moment and goes back from there; `limit` is the page
size.

## Page By Page

Iterate instead to process each page as it arrives, and stop whenever you have enough:

```python
from datetime import datetime, timedelta, timezone
from typed_nado import Nado

async with Nado.new(public=True) as client:
  cutoff = datetime.now(timezone.utc) - timedelta(days=30)
  candles = []
  async for page in client.archive.candlesticks_paged(product_id=2, granularity=3600):
    candles.extend(page)
    if page and page[-1]['timestamp'] < cutoff:
      break
```

## Public Trades

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  async for page in client.archive_v2.trades_paged('BTC-PERP_USDT0', limit=500):
    for trade in page:
      print(trade['trade_id'], trade['price'], trade['trade_type'])
```

## Retry And Resume

Each page is one independent read, so a walk can retry a failed page or pick up later
where it stopped. `via` routes every page fetch through your own wrapper, and `pages()`
exposes each page's state for checkpointing:

```python
from typed_nado import Nado, NetworkError

async def retried(fetch):
  """Retry one page fetch up to three times on network errors."""
  for attempt in range(3):
    try:
      return await fetch()
    except NetworkError:
      if attempt == 2:
        raise
  raise AssertionError('unreachable')

async with Nado.new(public=True) as client:
  walk = client.archive_v2.trades_paged('BTC-PERP_USDT0', limit=500)
  checkpoint = None
  async for page in walk.via(retried).pages():
    checkpoint = page.next  # save it; walk.resume(checkpoint) continues from here
    if checkpoint is None:
      break
```
