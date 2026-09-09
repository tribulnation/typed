# Paginate Through Results

`account.ledgers` returns one page:

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  page = await client.account.ledgers(currency='USDT', current_page=1, page_size=50)
  print(page['totalPage'], len(page['items']))
```

`account.ledgers_paged` walks every page automatically, from `current_page=1` up to
`totalPage`. Iterating it yields one page's `items` at a time; awaiting it flattens every
page into one list:

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  async for entries in client.account.ledgers_paged(currency='USDT', page_size=50):
    for entry in entries:
      print(entry['id'], entry['amount'])

  all_entries = await client.account.ledgers_paged(currency='USDT', page_size=50)
  print(len(all_entries))
```

To stop early, `break` out of the `async for`. The same page-number pattern applies to
`spot.orders_hf.get_open_orders_by_page`, `account.deposit.history_paged`,
`account.withdrawals.history_paged` and `earn.account_holding_paged`.

`spot.klines_paged` walks a time range instead: KuCoin keeps the newest 1500 candles of a
range it truncates, so the walk keeps your `start_at` fixed and moves `end_at` back to the
oldest candle of each full page until a page comes back short. Pages arrive newest first
and nothing outside your own `[start_at, end_at]` is ever requested. See
[Fetch Market Data](fetch-market-data.md).
