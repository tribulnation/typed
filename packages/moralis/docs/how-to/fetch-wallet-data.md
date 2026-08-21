# Fetch Wallet Data

Use `client.evm.wallet` for wallet-scoped EVM reads. Every method takes a wallet
`address` and a `chain`.

## Token Balances

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  balances = await client.evm.wallet.token_balances(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  print(balances['result'])
```

`token_balances` also takes `to_block` and `token_addresses` to restrict it to specific
contracts as of a given block.

## Transaction History

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  history = await client.evm.wallet.history(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  print(history['result'][0]['block_timestamp'])
```

Each transaction carries its decoded native, ERC20, and NFT transfers inline, and
`block_timestamp` is a real `datetime`. `history` also accepts `from_block`/`to_block`
or `from_date`/`to_date` range filters, and `order` (`'ASC'`/`'DESC'`).

## Token Transfers

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  transfers = await client.evm.wallet.token_transfers(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chain='eth',
  )
  print(transfers['result'])
```

`token_transfers` takes the same `from_block`/`to_block`/`from_date`/`to_date` filters as
`history`. `token_balances`, `history`, and `token_transfers` all return a `cursor` for the
next page, and all three have a `_paged` sibling; see
[Paginate Through Results](paginate-through-results.md).

## Net Worth And ENS

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  net_worth = await client.evm.wallet.wallet_net_worth(
    '0xd8dA6BF26964aF9D7eed9e03E53415D37aA96045', chains=['eth', 'polygon'],
  )
  address = await client.evm.wallet.resolve_address_from_ens_domain('vitalik.eth')
  print(net_worth.get('total_networth_usd'), address)
```

`wallet_net_worth` totals a wallet's USD value across the given `chains`, with options to
exclude spam/low-liquidity/inactive tokens. `resolve_address_from_ens_domain` (and its
inverse, `resolve_ens_domain_from_address`) resolve between an ENS domain and an address.
