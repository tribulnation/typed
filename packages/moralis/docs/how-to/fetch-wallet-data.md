# Fetch Wallet Data

Use `client.evm.wallet` for wallet-scoped reads: token balances, decoded transaction
history, and ERC20 transfers. Every method takes a wallet `address` and a `chain`.

## Token Balances

```python
from moralis import Moralis

async with Moralis.new() as client:
  balances = await client.evm.wallet.token_balances(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  print(balances['result'])
```

## Transaction History

```python
from moralis import Moralis

async with Moralis.new() as client:
  history = await client.evm.wallet.history(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  print(history['result'])
```

Each transaction carries its decoded native, ERC20, and NFT transfers inline.

## Token Transfers

```python
from moralis import Moralis

async with Moralis.new() as client:
  transfers = await client.evm.wallet.token_transfers(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  print(transfers['result'])
```

All three accept `from_date`/`to_date`/`from_block`/`to_block` filters and return a
`cursor` for the next page — see [Paginate Through Results](paginate-through-results.md).
