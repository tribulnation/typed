# Query Account Data

Balances, transaction history, and token transfers for an address. Every call here needs
`ETHERSCAN_API_KEY` — see [API keys setup](../api-keys.md).

## Native Balance

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  balance = await client.account.balance(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
  print(balance['result'])  # wei, as a string

  # several addresses at once -- one comma-separated `address` string
  multi = await client.account.balances(
    address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae,0xddbd2b932c763ba5b1b7ae3b362eac3e8d40121',
  )
```

It comes back in wei, the same as every native-value field on this API:

```python
from decimal import Decimal
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  balance = await client.account.balance(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
  eth = Decimal(balance['result']) / Decimal(10**18)
```

## Transaction History

Normal and internal transactions for an address, filtered by block range:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  txs = await client.account.transactions(
    address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae',
    startblock=0, endblock=99999999, sort='asc',
  )
  internal = await client.account.internal_transactions(
    address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae',
    startblock=0, endblock=99999999, sort='asc',
  )
```

## Token Transfers

ERC-20, ERC-721, and ERC-1155 transfer history. `erc20_transfers` and `erc721_transfers`
each require a `contractaddress` to scope to one token; `erc1155_transfers` takes none and
covers every ERC-1155 transfer for the address:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  erc20 = await client.account.erc20_transfers(
    address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae',
    contractaddress='0xdAC17F958D2ee523a2206206994597C13D831ec7',
  )
  erc721 = await client.account.erc721_transfers(
    address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae',
    contractaddress='0xdAC17F958D2ee523a2206206994597C13D831ec7',
  )
  erc1155 = await client.account.erc1155_transfers(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
```

## Mined Blocks

Blocks or uncles validated by a miner/validator address:

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  mined = await client.account.mined_blocks(
    address='0xea674fdde714fd979de3edf0f56aa9716b898ec8', blocktype='blocks',
  )
```

## Layer-2 Bridge Activity

`client.l2` covers the same per-address shape for bridge and beacon-chain activity, on the
chain selected by `chainid` (Polygon is `137`, for example):

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  bridge = await client.l2.plasma_deposits(
    chainid='137', address='0x4880bd4695a8e59dc527d124085749744b6c988',
  )
  withdrawals = await client.l2.beacon_withdrawals(address='0xde0b295669a9fd93d5f28d9ec85e40f4cb697bae')
```

Every method above also has a `_paged` variant — see
[Paginate through results](paginate-through-results.md).
