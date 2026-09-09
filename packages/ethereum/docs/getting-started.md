# Getting Started

Install the package:

```sh
pip install 'typed-ethereum>=0.2.0'
```

Read a public address without credentials:

```python
from typed_ethereum import NodeRpc

async with NodeRpc.public_node('ethereum') as client:
  balance = await client.eth_balance('0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe')
  print(balance)
```

`balance` is a `Decimal` in native-asset units, not wei. On other EVM networks,
`eth_balance` returns that network's native asset despite the method name.

Use `NodeRpc.at(rpc_url)` for your own HTTP endpoint. Keep the client inside
`async with` so its provider is disconnected on exit. Network and provider errors
propagate; see [Error Handling](reference/error-handling.md).
