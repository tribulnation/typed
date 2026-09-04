# Fetch Token Data

Use `client.evm.token` and `client.evm.price` for ERC20 contract-level lookups.

## Token Metadata

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  metadata = await client.evm.token.metadata.token_metadata(
    chain='eth', addresses=['0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'],
  )
  print(metadata[0]['symbol'])
```

`addresses` accepts multiple contract addresses per call.

## Token Price

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  price = await client.evm.price.token_price(
    'eth', address='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
  )
  print(price.get('usdPrice'))
```

## Token Score And Holders

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  score = await client.evm.token.metadata.token_score(
    'eth', token_address='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
  )
  holders = await client.evm.token.holders.token_holder_metrics(
    'eth', token_address='0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
  )
  print(score.get('score'), holders['totalHolders'])
```

`token_score` is Moralis's own spam/risk signal for a contract; `token_holder_metrics`
returns current holder counts and distribution. `evm.token.holders` also has
`top_token_holders` and a cursor-paginated `historical_token_holders`.
