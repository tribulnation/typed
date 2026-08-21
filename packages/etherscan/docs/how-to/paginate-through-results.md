# Paginate Through Results

Every list-returning `account`, `l2`, `logs`, and `tokens` method that takes `page`/`offset`
has a `_paged` sibling — an async generator that walks pages for you and stops on the first
page shorter than `offset`.

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  async for page in client.account.transactions_paged(
    address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae', offset=100,
  ):
    for tx in page['result']:
      print(tx.get('hash'))
```

`offset` is required for the walk to know what a "short," final page looks like — Etherscan
publishes no total count for these endpoints, so `_paged` methods use `short_page` as their
only stopping signal. Cap the walk with `max_pages` if you only want the first few pages:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  async for page in client.logs.by_address_paged(
    address='0xbd3531da5cf5857e7cfaa92426877b022e612cf8', offset=50, max_pages=3,
  ):
    ...
```

## One Page At A Time

The non-`_paged` method is still there whenever you'd rather manage pages yourself:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  first_page = await client.account.mined_blocks(
    address='0xea674fdde714fd979de3edf0f56aa9716b898ec8', page=1, offset=10,
  )
  second_page = await client.account.mined_blocks(
    address='0xea674fdde714fd979de3edf0f56aa9716b898ec8', page=2, offset=10,
  )
```
