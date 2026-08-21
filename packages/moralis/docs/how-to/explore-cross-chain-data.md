# Explore Cross-Chain Data

`client.universal` covers Moralis's chain-agnostic surface: entity search, market-wide
metrics, and trending tokens spanning multiple chains at once.

## Entity Search

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  found = await client.universal.entity.endpoints.entity_search(query='uniswap')
  print(found['result'].get('entities'))
```

An entity is an organization, project, or address cluster Moralis has linked together
(a protocol's known contracts, for example). `endpoints.entity(entity_id)` fetches one
entity's full profile by the `id` a search result returns.

## Chain And Category Metrics

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  chain_metrics = await client.universal.global_.endpoints.chain_metrics()
  category_metrics = await client.universal.global_.endpoints.category_metrics()
  print(chain_metrics, category_metrics)
```

Both are market-wide snapshots (volume, active addresses, ...), aggregated by chain and
by token category respectively; each also has a `*_timeseries` sibling for historical
data.

## Trending Tokens

```python
from typed_moralis import Moralis

async with Moralis.new() as client:
  trending = await client.universal.token.trending_tokens(chain='eth')
  print(trending[0]['symbol'])
```
