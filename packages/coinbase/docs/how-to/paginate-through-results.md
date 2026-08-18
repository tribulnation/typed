# Paginate Through Results

A paged endpoint has two forms on the same method: call it directly for one page, or its pager sibling for an async iterator that walks every page automatically. Pass `max_pages` to any pager to cap how many pages it walks.

## Coinbase App (v2)

```python
from coinbase import Coinbase

async with Coinbase.new() as client:
  page = await client.accounts.list(limit=25)          # one page
  print(page['data'])

  async for page in client.accounts.list.paged(limit=25):     # every page
    print(page['data'])

  async for page in client.accounts.transactions.list_paged('account-id', limit=25):
    print(page['data'])
```

## Advanced Trade (v3)

```python
from coinbase import Coinbase

async with Coinbase.new() as client:
  page = await client.advanced_trade.products.list(limit=50)
  print(page['products'])

  async for page in client.advanced_trade.products.list.paged(limit=50):
    print(page['products'])

  async for page in client.advanced_trade.orders.historical.batch_paged(order_status=['OPEN']):
    print(page['orders'])

  async for page in client.advanced_trade.orders.historical.fills_paged():
    print(page['fills'])
```
