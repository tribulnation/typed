# Fetch Bitcoin Data

`client.bitcoin` covers Bitcoin wallet balances/history, raw block/transaction lookups,
and BTC pricing, over a `chain_alias` of `'bitcoin'`/`'bitcoin-mainnet'`.

## Wallet Balances And History

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  balances = await client.bitcoin.wallet.btc_balances(wallet_address_or_public_key='bc1...')
  history = await client.bitcoin.wallet.wallet_history(wallet_address_or_public_key='bc1...')
  print(balances['result'], history['result'])
```

`btc_balances` also takes `chains` to fetch EVM-side balances held by the same address
where applicable, since Moralis links wallets across chain families. Both return a
`cursor` for the next page -- see [Paginate Through Results](paginate-through-results.md).

## Blocks And Transactions

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  block = await client.bitcoin.blockchain.block(block_identifier='800000', chain_alias='bitcoin')
  tx = await client.bitcoin.blockchain.transaction(tx_hash='tx_hash...', chain_alias='bitcoin')
  print(block['time'], tx)
```

`block_identifier` accepts either a block height or a block hash. `chain_alias` on both
methods also accepts `'0x89'`/`'polygon'`, since this endpoint pair is shared with EVM.

## Price And XPUB Addresses

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  price = await client.bitcoin.price.current_price('bitcoin-mainnet', token_alias_or_token_address='btc')
  derived = await client.bitcoin.utility.addresses_from_xpub('xpub...', chain_alias='bitcoin-mainnet')
  print(price['usdPrice'], derived['addresses'])
```
