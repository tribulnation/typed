# Paginate Through Results

`account.ledgers` returns one page:

```python
from kucoin import KuCoin

async with KuCoin.new() as client:
  page = await client.account.ledgers(currency='USDT', current_page=1, page_size=50)
  print(page['totalPage'], len(page['items']))
```

`account.ledgers_paged` walks every page automatically, from `current_page=1` up to
`totalPage`:

```python
from kucoin import KuCoin

async with KuCoin.new() as client:
  async for page in client.account.ledgers_paged(currency='USDT', page_size=50):
    for entry in page['items']:
      print(entry['id'], entry['amount'])
```

Pass `max_pages` to cap how far a `_paged` iterator walks. The same page-number pattern
applies to `spot.orders_hf.get_open_orders_by_page`,
`account.deposit.history_paged`, `account.withdrawals.history_paged` and
`earn.account_holding_paged`. `spot.klines_paged` is the exception: it instead walks a
time window forward until it gets an empty response — see
[Fetch Market Data](fetch-market-data.md).
