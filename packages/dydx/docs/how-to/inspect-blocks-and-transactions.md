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

Use `abci_query` to query application state through Comet, including protobuf
query routes when gRPC is unavailable:

```python
import base64

from typed_dydx import Dydx
from typed_dydx.protos.dydxprotocol.vault import QueryMegavaultTotalSharesRequest

request = QueryMegavaultTotalSharesRequest()

async with Dydx.kingnodes_archive(public=True) as client:
  result = await client.chain.comet.abci_query(
    path='/dydxprotocol.vault.Query/MegavaultTotalShares',
    data='0x' + bytes(request).hex(),
    height=100_000_000,
    prove=False,
  )
  response = result['response']
  if response['value'] is not None:
    response_bytes = base64.b64decode(response['value'])
    print(response['height'], response_bytes)
```

Pass an ordinary path; the client adds the JSON quotes required by Comet HTTP.
Request `data` is hex with a `0x` prefix, while response `value`, `key`, and proof
bytes are base64. Decode protobuf response bytes with the corresponding generated
response message. `prove=True` requests proofs only where the application route
supports them, such as `/store/vault/key`; `response['proofOps']` can be `None`.
A nonzero ABCI code raises `ApiError`, including when `validate=False`. The exception
retains the application's `code`, `codespace`, `log`, and other response fields.
HTTP and outer JSON-RPC errors raise the usual client exceptions.
