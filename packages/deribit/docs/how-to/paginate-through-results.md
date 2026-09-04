# Paginate Through Results

Endpoints the venue paginates get a `<method>_paged` async-iterator sibling beside the
single-request method, on the same router.

## Window Pagination

`market_data.get_mark_price_history` walks a `start_timestamp`/`end_timestamp` window
forward by its own width until a page comes back empty:

```python
from datetime import datetime, timezone
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  async for page in client.market_data.get_mark_price_history_paged(
    instrument_name='BTC-PERPETUAL',
    start_timestamp=datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc),
    end_timestamp=datetime(2023, 11, 14, 23, 13, 20, tzinfo=timezone.utc),
    max_pages=5,
  ):
    for mark_price, timestamp in page:
      print(timestamp, mark_price)
```

`max_pages` stops the walk early; omit it to walk the whole range.

## Offset Pagination

`wallet.deposits.get_deposits` pages by `count`/`offset`:

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  async for page in client.wallet.deposits.get_deposits_paged(
    currency='BTC', count=10,
  ):
    for deposit in page['data']:
      print(deposit['transaction_id'], deposit['amount'])
```

Both variants yield exactly what the single-request method returns, one page at a time —
the single-request method itself is always still there for a one-shot call.

## Token Pagination

`account.get_transaction_log` and seven other endpoints (`get_block_rfq_trades`,
`get_apr_history`, `get_last_settlements_by_currency`/`_by_instrument`,
`list_address_beneficiaries`, ...) walk a `continuation` token until the venue stops sending
one. Their `_paged` sibling returns a `PaginatedResponse` rather than a plain async
iterator — usable either as `async for` (one page's *rows* at a time, not the whole
response) or as an `await`, which flattens every page into a single list:

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

Unlike Window/Offset pagination, there's no `max_pages` — the walk stops on its own once
the venue sends no further `continuation` token.
