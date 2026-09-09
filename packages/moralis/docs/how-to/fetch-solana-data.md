# Fetch Solana Data

`client.solana.wallet` and `client.solana.token` mirror `evm`'s wallet/token split, over
Solana's own `mainnet`/`devnet` networks.

## Wallet Balances And Portfolio

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  native = await client.solana.wallet.native_balance('mainnet', address='address...')
  tokens = await client.solana.wallet.token_balances('mainnet', address='address...')
  portfolio = await client.solana.wallet.wallet_portfolio('mainnet', address='address...')
  print(native['solana'], tokens, portfolio['tokens'])
```

`native_balance` returns the SOL balance in lamports and SOL; `token_balances` returns
every SPL token the wallet holds; `wallet_portfolio` combines both plus NFTs in one call.

## Token Metadata

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  metadata = await client.solana.token.token_metadata('mainnet', address='mint_address...')
  print(metadata['name'], metadata['symbol'])
```

`solana.token` also has `pairs` (DEX pair data), `prices`, `holders`, and `swaps` for
deeper per-token analytics, over the same `network`/`address` shape.
