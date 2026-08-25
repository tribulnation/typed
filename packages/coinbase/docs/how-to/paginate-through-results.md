# Paginate Through Results

A paged endpoint has two forms on the same method: call it directly for one page, or its
pager sibling for every page. Every cursor-paginated pager below returns a
`PaginatedResponse` — `await` it to flatten every page into one list, or `async for` it to
walk one page (a list of rows) at a time; either way it stops on its own once the venue
stops returning a next cursor, with no `max_pages` to pass. `products.candles`' pager is
different (a time-window walk, not cursor pagination) — it stays a plain async generator
of whole response frames, and does take `max_pages` to cap how many windows it walks.

## Coinbase App (v2)

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  page = await client.app.accounts.list(limit=25)          # one page (the whole response frame)
  print(page['data'])

  accounts = await client.app.accounts.list.paged(limit=25)       # every account, flattened
  print(accounts[0]['id'])

  async for page in client.app.accounts.list.paged(limit=25):     # every page, one at a time
    for account in page:
      print(account['id'])

  transactions = await client.app.accounts.transactions.list_paged('account-id', limit=25)
  print(transactions[0]['id'])
```

## Advanced Trade (v3)

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  page = await client.app.advanced_trade.http.products.list(limit=50)
  print(page['products'])

  products = await client.app.advanced_trade.http.products.list.paged(limit=50)      # every product, flattened
  print(products[0]['product_id'])

  orders = await client.app.advanced_trade.http.orders.historical.batch_paged(order_status=['OPEN'])
  print(len(orders))

  fills = await client.app.advanced_trade.http.orders.historical.fills_paged()
  print(len(fills))
```
