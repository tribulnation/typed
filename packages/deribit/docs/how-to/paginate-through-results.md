# Paginate Through Results

Endpoints the venue paginates get a `<method>_paged` sibling beside the single-request
method, on the same router. Every one returns a `PaginatedResponse`: `async for` yields one
page's rows at a time (empty pages are skipped), and `await` flattens every page into one
list. The single-request method itself is always still there for a one-shot call.

## Seek Pagination

`market_data.get_funding_rate_history` takes a time range and returns at most the newest
744 hourly rows of it. Its `_paged` sibling therefore walks backwards: it moves
`end_timestamp` down to the earliest row timestamp of each full page, never past the
caller's own `start_timestamp`, and stops on the first page shorter than 744 rows. Pages
arrive newest-first; each row carries `timestamp`, `index_price`, `prev_index_price`,
`interest_8h` and `interest_1h`:

```python
from datetime import datetime, timezone
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  async for rows in client.market_data.get_funding_rate_history_paged(
    instrument_name='BTC-PERPETUAL',
    start_timestamp=datetime(2026, 6, 1, tzinfo=timezone.utc),
    end_timestamp=datetime(2026, 9, 1, tzinfo=timezone.utc),
  ):
    for row in rows:
      print(row['timestamp'], row['interest_8h'])
```

`market_data.get_mark_price_history` is not paginated: the venue only holds the most recent
few minutes of mark prices for an instrument, so a single call returns everything there is.

## Offset Pagination

`wallet.deposits.get_deposits` pages by `count`/`offset`. The `_paged` sibling advances
`offset` by the rows it received and stops once it has covered the `records_total` the
venue reports, yielding the `data` rows of each page rather than the whole response:

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  async for deposits in client.wallet.deposits.get_deposits_paged(
    currency='BTC', count=10,
  ):
    for deposit in deposits:
      print(deposit['transaction_id'], deposit['amount'])
```

## Token Pagination

`account.get_transaction_log` and seven other endpoints (`get_block_rfq_trades`,
`get_apr_history`, `get_last_settlements_by_currency`/`_by_instrument`,
`list_address_beneficiaries`, ...) walk a `continuation` token until the venue stops sending
one:

```python
from datetime import datetime, timezone
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  paged = client.account.get_transaction_log_paged(
    currency='BTC',
    start_timestamp=datetime(2025, 8, 8, 20, 15, 12, tzinfo=timezone.utc),
    end_timestamp=datetime(2026, 8, 8, 20, 15, 12, tzinfo=timezone.utc),
    count=10,
  )

  # one page (a list of rows) at a time:
  async for rows in paged:
    for entry in rows:
      print(entry['id'], entry['timestamp'], entry.get('cashflow'))

  # or flatten every page into one list:
  all_entries = await client.account.get_transaction_log_paged(
    currency='BTC',
    start_timestamp=datetime(2025, 8, 8, 20, 15, 12, tzinfo=timezone.utc),
    end_timestamp=datetime(2026, 8, 8, 20, 15, 12, tzinfo=timezone.utc),
    count=10,
  )
```

## Stopping Early, Checkpointing, Resuming

There is no page cap keyword: `break` out of `async for` to stop early. For a long walk,
`.pages()` yields each page with the state it was fetched with and the state of the page
after it, and `.resume(state)` restarts the same walk from a saved one:

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  paged = client.market_data.get_delivery_prices_paged(index_name='btc_usd', count=100)
  checkpoint: int | None = None
  async for page in paged.pages():
    print(len(page.rows), 'rows, next offset', page.next)
    if page.next is not None and page.next >= 200:
      checkpoint = page.next
      break

  if checkpoint is not None:
    remaining = await paged.resume(checkpoint)
```
