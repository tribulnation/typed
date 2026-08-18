# Query & Manage Earn Instruments

`spot.earn` -- private, see [API Keys Setup](../api-keys.md) first.

## List Strategies

```python
from kraken import Kraken

async with Kraken.new() as client:
  strategies = await client.spot.earn.strategies()
```

Each strategy carries a `strategy_id`, the asset it earns on, and its lock type
(`flex`, `bonded`, `timed`, or `instant`) -- pass that id to `allocate`/`deallocate`.

## List Your Allocations

```python
from kraken import Kraken

async with Kraken.new() as client:
  allocations = await client.spot.earn.allocations()
```

Your current Earn subscriptions, one entry per strategy you've allocated funds to.

## Subscribe & Redeem

```python
from kraken import Kraken

async with Kraken.new() as client:
  await client.spot.earn.allocate(strategy_id='...', amount='5')
  status = await client.spot.earn.allocate_status(strategy_id='...')
  await client.spot.earn.deallocate(strategy_id='...', amount='5')
  d_status = await client.spot.earn.deallocate_status(strategy_id='...')
```

`allocate`/`deallocate` request funds move into or out of a strategy; both are
asynchronous on Kraken's side, so `allocate_status`/`deallocate_status` poll whether the
pending request has completed (`bonded`/`timed` strategies can take a while).
