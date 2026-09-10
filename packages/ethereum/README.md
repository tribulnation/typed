# Typed Ethereum

Async EVM node access through `NodeRpc`, a small wrapper around Web3.py.
Native and ERC-20 balance helpers return `Decimal`; `.w3` exposes the underlying
`AsyncWeb3` connection.

```python
from typed_ethereum import NodeRpc

async with NodeRpc.public_node('ethereum') as client:
  balance = await client.eth_balance('0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe')
  print(balance)
```

Public nodes require no credentials. See [Getting Started](docs/getting-started.md)
and [API Overview](docs/api-overview.md) for the supported surface and limitations.

Version 0.2 imports from `typed_ethereum`, replacing the former `ethereum` namespace.
The client remains in beta.
The package installed by pip remains `typed-ethereum`.
