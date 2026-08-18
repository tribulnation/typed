# Manage Account Data

dYdX account state is split across wallet-level chain accounts and
subaccount-level trading state. Use chain modules for wallet balances and
protocol state; use the indexer for trading history, fills, transfers, and
positions.

```python
from dydx import Dydx

async with Dydx.testnet(public=True) as client:
  balances = await client.chain.bank.all_balances('dydx1...')
  print(balances)
```

Subaccount trading state is available from both the indexer and chain modules:

```python
from dydx import Dydx

address = 'dydx1...'

async with Dydx.testnet(public=True) as client:
  subaccount = await client.indexer.data.get_subaccount(address, subaccount=0)
  chain_subaccount = await client.chain.subaccounts.subaccount(address, 0)
  print(subaccount, chain_subaccount)
```

For history, use the indexer:

```python
from dydx import Dydx

address = 'dydx1...'

async with Dydx.testnet(public=True) as client:
  fills = await client.indexer.data.get_fills(address, subaccount=0, limit=100)
  transfers = await client.indexer.data.get_transfers(address, subaccount=0, limit=100)
  positions = await client.indexer.data.list_positions(address, subaccount=0)
  print(fills, transfers, positions)
```

Read-only account workflows can use `public=True`. Signed workflows need a
mnemonic; see [Wallet Setup](../api-keys.md).
