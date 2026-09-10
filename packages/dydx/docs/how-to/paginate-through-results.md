# Paginate Through Results

Endpoints the venue paginates get a `<method_name>_paged(...)` sibling returning a
`PaginatedResponse`: `async for` yields one page's rows at a time (empty pages are skipped),
and `await` flattens every page into one list.

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  async for fills in client.indexer.data.get_fills_paged(
    address='dydx1...',
    subaccount=0,
    limit=100,
  ):
    for fill in fills:
      print(fill['id'], fill['price'])

  # or flatten every page into one list:
  all_fills = await client.indexer.data.get_fills_paged(
    address='dydx1...',
    subaccount=0,
    limit=100,
  )

  # the single-request method is still there for one page:
  first_page = await client.indexer.data.get_fills(
    address='dydx1...',
    subaccount=0,
    page=1,
  )
```

## Time And Height Ranges

`indexer.data.get_candles` and `get_historical_funding` are walked newest-first: the paged
sibling moves `to_iso` (respectively `effective_before_or_at_height`) down to the earliest
row of each page it receives, never past the caller's own `from_iso`, drops the boundary row
the venue serves again, and stops on the first page that brings nothing new. Funding rows
sharing one block height are kept apart by content, so a shared height is neither
duplicated nor skipped.

```python
from datetime import datetime, timezone
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  candles = await client.indexer.data.get_candles_paged(
    'BTC-USD',
    resolution='1HOUR',
    from_iso=datetime(2026, 8, 1, tzinfo=timezone.utc),
    to_iso=datetime(2026, 8, 2, tzinfo=timezone.utc),
  )
  for candle in reversed(candles):  # oldest first
    print(candle['startedAt'], candle['close'])
```

## Stopping Early, Checkpointing, Resuming

There is no page cap keyword: `break` out of `async for` to stop early. For a long walk,
`.pages()` yields each page with the state it was fetched with and the state of the page
after it, and `.resume(state)` restarts the same walk from a saved one:

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  paged = client.indexer.data.get_transfers_paged('dydx1...', subaccount=0, limit=100)
  checkpoint: int | None = None
  async for page in paged.pages():
    print(len(page.rows), 'rows, next page', page.next)
    if page.next is not None and page.next > 3:
      checkpoint = page.next
      break

  if checkpoint is not None:
    remaining = await paged.resume(checkpoint)
```
