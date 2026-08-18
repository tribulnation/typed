# Fetch Token Data

Use `client.evm.token` for ERC20 contract-level lookups.

## Token Metadata

```python
from moralis import Moralis

async with Moralis.new() as client:
  metadata = await client.evm.token.metadata(
    addresses=['0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'], chain='eth',
  )
  print(metadata[0]['symbol'])
```

`addresses` accepts up to 10 contract addresses per call.
