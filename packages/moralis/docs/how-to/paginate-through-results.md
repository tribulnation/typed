# Paginate Through Results

`client.evm.wallet.history`, `.token_balances`, and `.token_transfers` all return a
`cursor` for the next page. Each has a `_paged` counterpart that walks the cursor for you.

```python
from moralis import Moralis

async with Moralis.new() as client:
  first_page = await client.evm.wallet.token_balances(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  print(first_page['result'])
```

`token_balances_paged(...)` returns an async iterable of balance pages:

```python
from moralis import Moralis

async with Moralis.new() as client:
  pages = client.evm.wallet.token_balances_paged(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  async for balances in pages:
    print(balances)
```

You can also await a paginated response to flatten every page into one list:

```python
from moralis import Moralis

async with Moralis.new() as client:
  balances = await client.evm.wallet.token_balances_paged(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  print(balances)
```

`history_paged(...)` and `token_transfers_paged(...)` work the same way, over
`client.evm.wallet.history` and `client.evm.wallet.token_transfers` respectively.
`client.evm.token.metadata` is not paginated.
