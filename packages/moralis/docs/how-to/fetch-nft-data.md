# Fetch NFT Data

`client.evm.wallet.nft_balances` lists the NFTs a wallet holds; `client.evm.nft`'s
subgroups cover contract- and token-level lookups.

## NFTs In A Wallet

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  owned = await client.evm.wallet.nft_balances(
    'eth', address='0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045',
  )
  print(owned['result'])
```

Each entry includes on-chain and off-chain metadata, floor price, and rarity where
available. Pass `token_addresses` to restrict this to specific collections.

## NFT And Collection Metadata

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  nft = await client.evm.nft.metadata.nft_metadata(
    'eth', address='0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D', token_id='1',
  )
  collection = await client.evm.nft.metadata.collection_metadata(
    'eth', address='0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D',
  )
  print(nft.get('name'), collection.get('name'))
```

## Ownership, Prices, And Trades

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  owners = await client.evm.nft.ownership.owners_by_collection(
    'eth', address='0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D',
  )
  floor = await client.evm.nft.prices.floor_price_by_collection(
    'eth', address='0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D',
  )
  trades = await client.evm.nft.trades.nft_trades_by_collection(
    'eth', address='0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D',
  )
  print(owners['walletAddresses'], floor, trades['result'])
```

`evm.nft.discovery` (trending collections) and `evm.nft.traits` (trait rarity) cover the
rest of the collection-analytics surface the same way.
