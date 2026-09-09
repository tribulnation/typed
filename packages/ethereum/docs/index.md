# Typed Ethereum

`NodeRpc` provides async EVM node access through Web3.py, with `Decimal` helpers
for native and ERC-20 balances. It is not an exchange client: there is no
`Ethereum.new()`, ticker, trading namespace, or client-level `validate` switch.

```python
from typed_ethereum import NodeRpc

async with NodeRpc.public_node('ethereum') as client:
  balance = await client.eth_balance('0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe')
  print(balance)
```

1. [Getting Started](getting-started.md)
2. [RPC Provider Credentials](api-keys.md)
3. [API Overview](api-overview.md)
4. [How To](how-to/index.md)
5. [Reference](reference/index.md)

## Migrating to 0.2

Replace `from ethereum import NodeRpc` with `from typed_ethereum import NodeRpc`.
The pip distribution name remains `typed-ethereum`.
