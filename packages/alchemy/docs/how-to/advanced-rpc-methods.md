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

## HyperEVM and product availability

The chain RPC groups accept `network='hyperevm'`, selecting
`https://hyperliquid-mainnet.g.alchemy.com/v2/{apiKey}`. A network selector chooses a host;
it does not guarantee that every enhanced method is supported there. Check Alchemy's
[feature support by chain](https://www.alchemy.com/docs/reference/feature-support-by-chain)
for the method you need. The client has no default HyperEVM NFT URL;
`client.nft(network='hyperevm')` raises `ValueError`. An explicit `base_url` overrides
host selection when you have a suitable endpoint.

## Standard node RPC with Web3.py

Alchemy's EVM nodes expose standard Ethereum JSON-RPC. Use Web3.py directly for
`eth_getLogs`, `eth_getCode`, `eth_getStorageAt`, and `eth_call`, including historical
block identifiers. Typed Alchemy provides the enhanced APIs shown above; it does not
provide a separate node client or require Web3.py.

Install Web3.py separately:

```bash
pip install 'web3>=7.7,<8'
```

With `ALCHEMY_API_KEY` configured, this example reads Ethereum state at one block and
batches two further reads. For HyperEVM, change the host to
`hyperliquid-mainnet.g.alchemy.com` and choose an address on that chain.

```python
import os
from web3 import AsyncHTTPProvider, AsyncWeb3, Web3

provider = AsyncHTTPProvider(
  f'https://eth-mainnet.g.alchemy.com/v2/{os.environ["ALCHEMY_API_KEY"]}',
)
w3 = AsyncWeb3(provider)
address = Web3.to_checksum_address('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48')
try:
  block = await w3.eth.block_number
  logs = await w3.eth.get_logs({
    'address': address, 'fromBlock': block, 'toBlock': block,
  })
  code = await w3.eth.get_code(address, block_identifier=block)
  storage = await w3.eth.get_storage_at(address, 0, block_identifier=block)
  result = await w3.eth.call(
    {'to': address, 'data': bytes.fromhex('18160ddd')}, block_identifier=block,
  )  # ERC-20 totalSupply()
  async with w3.batch_requests() as batch:
    batch.add(w3.eth.get_code(address, block_identifier=block))
    batch.add(w3.eth.get_storage_at(address, 0, block_identifier=block))
    responses = await batch.async_execute()
finally:
  await provider.disconnect()
```

### Trace calls and raw responses

Use the provider's `make_request` for custom methods and decoded JSON-RPC envelopes.
For example, an application can supply a transaction hash to this helper:

```python
from web3 import AsyncHTTPProvider
from web3.types import RPCEndpoint

async def trace_with_logs(provider: AsyncHTTPProvider, transaction_hash: str):
  return await provider.make_request(
    RPCEndpoint('debug_traceTransaction'),
    [transaction_hash, {'tracer': 'callTracer', 'tracerConfig': {'withLog': True}}],
  )
```

Call `trace_filter` the same way, passing a one-element list containing its filter
object. These methods and tracer options depend on the network and Alchemy plan.
Provider calls bypass Web3's usual middleware and result formatting: inspect the
returned `error` or `result` yourself. They return decoded JSON, not original HTTP
response bytes, and cannot be added to Web3's high-level batch context.

Alchemy also restricts batching for some enhanced and trace/debug methods. See
[Web3 batching](https://web3py.readthedocs.io/en/v7.14.0/web3.main.html#batch-requests)
and [Alchemy batching](https://www.alchemy.com/docs/reference/batch-requests).

### Compute units and diagnostics

Meter Alchemy compute units in your application using its
[CU cost table](https://www.alchemy.com/docs/reference/compute-unit-costs).
Billing CU and throughput CU can differ. Count each batch member and actual retry;
a local cost-table estimate is not an authoritative billing total.

Web3 owns its connection, errors and logging separately. Typed Alchemy's credential
redaction applies to requests made through Typed Alchemy, not this separate provider.
