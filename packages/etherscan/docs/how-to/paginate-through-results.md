# Paginate Through Results

Every list-returning `account`, `l2`, `logs`, and `tokens` method that takes `page`/`offset`
has a `_paged` sibling. Each one returns a `PaginatedResponse`: `async for` it to get one
page's `result` rows at a time, or `await` it to flatten every page into a single list. The
walk stops on the first page shorter than `offset`, or on an empty page.

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  async for txs in client.account.transactions_paged(
    address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae', offset=100,
  ):
    for tx in txs:
      print(tx.get('hash'))
```

`offset` is required for the walk to know what a "short," final page looks like: Etherscan
publishes no total count for these endpoints, so `_paged` methods use `short_page` as their
stopping signal. The rows are the envelope's `result` list, already unwrapped, so you never
index past `status`/`message` yourself.

## Flatten Everything

Awaiting the same response walks every page and concatenates the rows:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  logs = await client.logs.by_address_paged(
    address='0xbd3531da5cf5857e7cfaa92426877b022e612cf8', offset=1000,
  )
  print(len(logs))
```

## Stop Early

There is no page cap keyword. To take only the first few pages, `break` out of the loop:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  seen = 0
  async for logs in client.logs.by_address_paged(
    address='0xbd3531da5cf5857e7cfaa92426877b022e612cf8', offset=50,
  ):
    seen += 1
    if seen == 3:
      break
```

## Checkpoint And Resume

`.pages()` yields each page with the page index it was fetched at (`state`) and the one the
next page will use (`next`, `None` after the last page). Save `next` to pick a long walk up
later with `.resume()`:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  paging = client.account.transactions_paged(
    address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae', offset=100,
  )
  last_next: int | None = None
  async for page in paging.pages():
    last_next = page.next
    if page.next == 3:
      break

  if last_next is not None:
    remaining = await paging.resume(last_next)
    print(len(remaining))
```

## One Page At A Time

The non-`_paged` method is still there whenever you'd rather manage pages yourself; it
returns the full `EtherscanResponse` envelope:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  first_page = await client.account.mined_blocks(
    address='0xea674fdde714fd979de3edf0f56aa9716b898ec8', page=1, offset=10,
  )
  second_page = await client.account.mined_blocks(
    address='0xea674fdde714fd979de3edf0f56aa9716b898ec8', page=2, offset=10,
  )
  print(first_page['result'], second_page['result'])
```
