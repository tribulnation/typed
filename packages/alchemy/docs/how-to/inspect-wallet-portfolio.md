# Inspect Wallet Portfolio

Use `client.portfolio` for wallet-level Portfolio API methods. Portfolio
requests use Alchemy network names such as `eth-mainnet`.

## Token Balances

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  balances = await client.portfolio.token_balances(
    addresses=[
      {
        'address': '0x1E6E8695FAb3Eb382534915eA8d7Cc1D1994B152',
        'networks': ['eth-mainnet'],
      }
    ],
    include_native_tokens=True,
    include_erc20tokens=True,
    page_size=2,
  )
  print(balances['data']['tokens'])
```

## NFT Holdings

Pass `with_metadata=True` explicitly to get full NFT metadata (name, image, collection,
etc.) in each returned item. Alchemy's own docs describe `withMetadata` as defaulting to
`true`, but the live API actually defaults to `false`: omitting it returns a minimal row
(just `address`, `balance`, `contractAddress`, `isSpam`, `network`, `spamClassifications`,
`tokenId`), with none of the metadata fields. `client.portfolio.nft_contracts` has the
same real default.

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  nfts = await client.portfolio.nfts(
    addresses=[
      {
        'address': '0x1E6E8695FAb3Eb382534915eA8d7Cc1D1994B152',
        'networks': ['eth-mainnet'],
        'excludeFilters': ['SPAM'],
        'spamConfidenceLevel': 'VERY_HIGH',
      }
    ],
    with_metadata=True,
    page_size=2,
    order_by='transferTime',
    sort_order='asc',
  )
  print(nfts['data']['ownedNfts'])
```

## Transaction History

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  history = await client.portfolio.transactions.history(
    addresses=[
      {
        'address': '0x1E6E8695FAb3Eb382534915eA8d7Cc1D1994B152',
        'networks': ['eth-mainnet'],
      }
    ],
    limit=2,
  )
  print(history['transactions'])
```
