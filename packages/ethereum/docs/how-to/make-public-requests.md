# Read Public Balances

```python
from typed_ethereum import NodeRpc

async with NodeRpc.public_node('ethereum') as client:
  balance = await client.eth_balance('0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe')
  print(balance)
```

No credential is required. The returned `Decimal` uses native-asset units.
For ERC-20 balances, use the helpers listed in [API Overview](../api-overview.md).
The client does not discover tokens held by an address.
