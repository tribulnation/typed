# Paginate Through Results

Every cursor-paginated Moralis endpoint -- `evm.wallet.token_balances`,
`bitcoin.wallet.btc_balances`, `streams.evm.all_streams`, and dozens more across every
product -- has a `_paged` sibling method. Each is `PaginatedResponse`-shaped: usable both
as `async for` (one page at a time) and as `await` (flattened into one list), walking the
venue's `cursor` for you until it comes back empty.

## Async Iteration

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  pages = client.evm.wallet.token_balances_paged(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  async for balances in pages:
    print(balances)
```

## Awaiting The Full Result

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  balances = await client.evm.wallet.token_balances_paged(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  print(balances)
```

`balances` here is every row from every page, flattened -- no need to concatenate pages
yourself. There is no page cap; the walk stops once the API reports no next cursor.

## Elsewhere In The Client

The same pattern applies unchanged wherever a `_paged` method exists, for example:

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  history = await client.evm.wallet.history_paged(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  btc = await client.bitcoin.wallet.btc_balances_paged('bc1...')
  streams = await client.streams.evm.all_streams_paged(limit=100)
```

An endpoint with no natural cursor to walk -- `evm.token.metadata.token_metadata`,
`solana.wallet.native_balance` -- has no `_paged` sibling; call it directly.
