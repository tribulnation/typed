# Advanced RPC Methods

Typed Alchemy also exposes token, utility, and simulation JSON-RPC methods. Use
the network selector for each group.

## Token Metadata

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  metadata = await client.token(network='ethereum').get_token_metadata(
    '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48',
  )
  print(metadata)
```

## Token Balances

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  balances = await client.token(network='ethereum').get_token_balances(
    address='0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
    token_spec='erc20',
    max_count=5,
  )
  print(balances['tokenBalances'])
```

## Transaction Receipts

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  receipts = await client.utility(network='ethereum').get_transaction_receipts(
    block_number='0xF1D1C6',
  )
  print(receipts['receipts'])
```

## Simulate Asset Changes

```python
from typed_alchemy import Alchemy

async with Alchemy.new() as client:
  changes = await client.simulation(network='ethereum').asset_changes({
    'from': '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
    'to': '0x1E6E8695FAb3Eb382534915eA8d7Cc1D1994B152',
    'value': '0xDE0B6B3A7640000',
    'gas': '0x5208',
  })
  print(changes['changes'])
```
