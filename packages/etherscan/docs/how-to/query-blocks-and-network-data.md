# Query Blocks & Network Data

Block-level lookups, chain-wide stats, and gas estimates.

## Blocks

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  reward = await client.blocks.reward(blockno=2165403)          # block + uncle rewards
  countdown = await client.blocks.countdown(blockno=25038851)   # ETA to a future block
```

`number_by_time` takes a real `datetime` — it's typed `TimestampSeconds`, converted to a
Unix-seconds timestamp on the wire:

```python
from datetime import datetime, timezone
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  closest = await client.blocks.number_by_time(
    timestamp=datetime(2020, 1, 10, tzinfo=timezone.utc), closest='before',
  )
```

## Network Stats

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  price = await client.stats.eth_price()
  supply = await client.stats.eth_supply()
  size = await client.stats.chain_size()
  nodes = await client.stats.node_count()
```

Historical/statistical variants of these (`stats.daily_transactions`,
`stats.eth_daily_price`, ...) are real methods too, but Etherscan gates them behind a paid
plan — they raise `ApiError` on the free tier.

## Gas Tracker

```python
from typed_etherscan import Etherscan

async with Etherscan.new() as client:
  oracle = await client.gas_tracker.oracle()                          # current safe/propose/fast prices
  eta = await client.gas_tracker.confirmation_time(gasprice='20000000000')  # ETA at a given price, in wei
```

## Chain Selection

Every method above takes an optional `chainid`, defaulting to Ethereum mainnet server-side
when omitted. Pass the chain ID of any network the V2 API supports, e.g. `chainid='137'`
for Polygon, to query that chain instead — the full list is
`client.usage.chain_list()` (see [API keys setup](../api-keys.md#public-access)).
