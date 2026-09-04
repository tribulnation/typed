# Query NFTs

Use `client.nft(network='<network>')` for NFT API v3 methods. The network selector is
a typed literal such as `'ethereum'`, `'base'`, or `'polygon'`.

## NFTs Owned By A Wallet

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  nfts = await client.nft(network='ethereum').get_nfts_for_owner(
    owner='0x1E6E8695FAb3Eb382534915eA8d7Cc1D1994B152',
    page_size=2,
    with_metadata=True,
  )
  print(nfts.get('ownedNfts'))
```

## NFTs In A Contract

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  nfts = await client.nft(network='ethereum').get_nfts_for_contract(
    contract_address='0xe785E82358879F061BC3dcAC6f0444462D4b5330',
    limit=2,
    with_metadata=True,
  )
  print(nfts.get('nfts'))
```

## Collection Metadata

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  collection = await client.nft(network='ethereum').get_collection_metadata(
    collection_slug='world-of-women-nft',
  )
  print(collection.get('name'))
```
