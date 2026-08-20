# Paginate Through Results

Endpoints that page results expose a `_paged` sibling (or a `.paged(...)` method, for the
Portfolio endpoint objects). Each one is `PaginatedResponse`-shaped: **both** awaitable
and async-iterable, never just one or the other.

- `await` it directly to collect every page into one flat list of rows.
- `async for` it to walk one page's rows at a time, without holding the whole series in
  memory at once.

Either way, what you get back is the *rows themselves* — the collection a page's response
carries (`transfers`, `data.tokens`, `ownedNfts`, ...) — not the raw per-page response
object.

## Transfers

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  transfers = await client.transfers('ethereum').get_asset_transfers_paged({
    'fromBlock': '0x0',
    'toAddress': '0x5c43B1eD97e52d009611D89b74fA829FE4ac56b1',
    'category': ['external'],
    'maxCount': '0x2',
  })
  print(len(transfers))
```

## Portfolio

Portfolio endpoints are callable field objects; their pagination lives on `.paged(...)`:

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  pages = client.portfolio.tokens.paged({
    'addresses': [
      {
        'address': '0x1E6E8695FAb3Eb382534915eA8d7Cc1D1994B152',
        'networks': ['eth-mainnet'],
      }
    ],
    'pageSize': 10,
  })
  async for tokens in pages:
    print(tokens)
```

## NFT And Token

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  owned_nfts = await client.nft('ethereum').get_nfts_for_owner_paged(
    owner='vitalik.eth',
    page_size=10,
  )
  print(len(owned_nfts))

  balance_pages = client.token('ethereum').get_token_balances_paged(
    '0x1E6E8695FAb3Eb382534915eA8d7Cc1D1994B152',
    'erc20',
    max_count=10,
  )
  async for balances in balance_pages:
    print(balances)
```

## Choosing `await` Vs. `async for`

`await` is the simpler default when the total result set is small enough to hold in
memory — a wallet's token balances, say. `async for` is the better fit for a series that
can run long — an active contract's full transfer history — since it never buffers more
than one page at a time:

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  pages = client.transfers('ethereum').get_asset_transfers_paged(
    {'category': ['external'], 'toAddress': '0x5c43B1eD97e52d009611D89b74fA829FE4ac56b1'},
  )
  async for transfers in pages:
    for transfer in transfers:
      print(transfer['hash'])
```
