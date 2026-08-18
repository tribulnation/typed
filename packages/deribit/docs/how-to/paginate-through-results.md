# Paginate Through Results

Endpoints the venue paginates get a `<method>_paged` async-iterator sibling beside the
single-request method, on the same router.

## Window Pagination

`market_data.get_mark_price_history` walks a `start_timestamp`/`end_timestamp` window
forward by its own width until a page comes back empty:

```python
from deribit import Deribit

async with Deribit.new(public=True) as client:
  async for page in client.http.market_data.get_mark_price_history_paged(
    instrument_name='BTC-PERPETUAL',
    start_timestamp=1700000000000,
    end_timestamp=1700003600000,
    max_pages=5,
  ):
    for mark_price, timestamp in page:
      print(timestamp, mark_price)
```

`max_pages` stops the walk early; omit it to walk the whole range.

## Offset Pagination

`wallet.deposits.get_deposits` pages by `count`/`offset`:

```python
from deribit import Deribit

async with Deribit.new(testnet=True) as client:
  async for page in client.http.wallet.deposits.get_deposits_paged(
    currency='BTC', count=10,
  ):
    for deposit in page['data']:
      print(deposit['transaction_id'], deposit['amount'])
```

Both variants yield exactly what the single-request method returns, one page at a time —
the single-request method itself is always still there for a one-shot call.
