# Query Chain State

Use `client.chain` for read-only Cosmos gRPC queries and dYdX protocol module
queries. These calls read node state directly instead of going through the
indexer.

```python
from dydx import Dydx

address = 'dydx1...'

async with Dydx.testnet(public=True) as client:
  account = await client.chain.auth.account(address)
  balances = await client.chain.bank.all_balances(address, resolve_denom=False)
  dydx_metadata = await client.chain.bank.denom_metadata('adydx')
  print(account, balances, dydx_metadata)
```

List endpoints also expose paged wrappers that use Cosmos continuation keys:

```python
from dydx import Dydx

address = 'dydx1...'

async with Dydx.testnet(public=True) as client:
  balances = await client.chain.bank.all_balances_paged(address, resolve_denom=False, limit=100)

  async for page in client.chain.staking.validators_paged('BOND_STATUS_BONDED', limit=50):
    print(page)
```

dYdX trading state is organized by subaccounts:

```python
from dydx import Dydx

address = 'dydx1...'

async with Dydx.testnet(public=True) as client:
  subaccount = await client.chain.subaccounts.subaccount(address, number=0)
  collateral_pool = await client.chain.subaccounts.collateral_pool_address(0)
  print(subaccount, collateral_pool)
```

Protocol metadata is grouped by module:

```python
from dydx import Dydx

async with Dydx.testnet(public=True) as client:
  clob_pair = await client.chain.clob.clob_pair(0)
  all_pairs = await client.chain.clob.clob_pairs()
  price = await client.chain.prices.market_price(0)
  perpetual = await client.chain.perpetuals.perpetual(0)
  assets = await client.chain.assets.assets()
  print(clob_pair, all_pairs, price, perpetual, assets)
```

Other chain modules expose staking, distribution, fee-tier, reward, affiliate,
and revenue-share reads under `client.chain.staking`, `client.chain.distribution`,
`client.chain.feetiers`, `client.chain.rewards`, `client.chain.affiliates`, and
`client.chain.revshare`.
