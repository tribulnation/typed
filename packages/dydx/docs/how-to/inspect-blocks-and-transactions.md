# Inspect Blocks and Transactions

Use the Cosmos Tendermint gRPC service for current block metadata and Comet RPC
for block results, transaction lookup, and transaction search.

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  latest = await client.chain.tendermint.get_latest_block()
  node_info = await client.chain.tendermint.get_node_info()
  print(latest, node_info)
```

Comet RPC exposes block and event-level data that is useful for verification
and accounting workflows:

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  status = await client.chain.comet.status()
  block = await client.chain.comet.block()
  block_results = await client.chain.comet.block_results()
  print(status['sync_info'], block['block_id'], block_results.get('height'))
```

Lookup a transaction by hash through either Cosmos gRPC or Comet RPC:

```python
from typed_dydx import Dydx

tx_hash = '...'

async with Dydx.testnet(public=True) as client:
  tx = await client.chain.tx.get_tx(tx_hash)
  comet_tx = await client.chain.comet.tx(tx_hash)
  print(tx, comet_tx)
```

Use Comet transaction search when you need event-based history:

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  txs = await client.chain.comet.tx_search_paged(
    'message.sender=\'dydx1...\'',
    per_page=25,
    order_by='asc',
  )
  print(txs)
```

For historical backfills, prefer archive constructors such as
`Dydx.polkachu_archive(public=True)` or `Dydx.kingnodes_archive(public=True)`
when the requested height may be pruned from regular nodes.
