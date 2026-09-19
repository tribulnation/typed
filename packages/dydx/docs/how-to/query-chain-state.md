# Query Chain State

Use `client.chain` for read-only Cosmos gRPC queries and dYdX protocol module
queries. These calls read node state directly instead of going through the
indexer.

```python
from typed_dydx import Dydx

address = 'dydx1...'

async with Dydx.testnet(public=True) as client:
  account = await client.chain.auth.account(address)
  balances = await client.chain.bank.all_balances(address, resolve_denom=False)
  dydx_metadata = await client.chain.bank.denom_metadata('adydx')
  print(account, balances, dydx_metadata)
```

List endpoints also expose paged wrappers that use Cosmos continuation keys:

```python
from typed_dydx import Dydx

address = 'dydx1...'

async with Dydx.testnet(public=True) as client:
  balances = await client.chain.bank.all_balances_paged(address, resolve_denom=False, limit=100)

  async for page in client.chain.staking.validators_paged('BOND_STATUS_BONDED', limit=50):
    print(page)
```

dYdX trading state is organized by subaccounts:

```python
from typed_dydx import Dydx

address = 'dydx1...'

async with Dydx.testnet(public=True) as client:
  subaccount = await client.chain.subaccounts.subaccount(address, number=0)
  collateral_pool = await client.chain.subaccounts.collateral_pool_address(0)
  print(subaccount, collateral_pool)
```

Protocol metadata is grouped by module:

```python
from typed_dydx import Dydx

async with Dydx.testnet(public=True) as client:
  clob_pair = await client.chain.clob.clob_pair(0)
  all_pairs = await client.chain.clob.clob_pairs()
  price = await client.chain.prices.market_price(0)
  perpetual = await client.chain.perpetuals.perpetual(0)
  assets = await client.chain.assets.all()
  print(clob_pair, all_pairs, price, perpetual, assets)
```

Other chain modules expose staking, distribution, fee-tier, reward, affiliate,
and revenue-share reads under `client.chain.staking`, `client.chain.distribution`,
`client.chain.feetiers`, `client.chain.rewards`, `client.chain.affiliates`, and
`client.chain.revshare`.

MegaVault share accounting is available under `chain.vault`:

```python
from typed_dydx.chain import Chain

address = 'dydx1...'

async with Chain.kingnodes_archive() as chain:
  total = await chain.vault.megavault_total_shares()
  owner = await chain.vault.megavault_owner_shares(address)
  print(total.total_shares, owner.shares, owner.share_unlocks)

  async for owners in chain.vault.megavault_all_owner_shares_paged(limit=50):
    print(owners)
```

`all_vaults_paged` traverses individual market vaults; `get` and `vault_params`
look up a vault by type and number. `megavault_withdrawal_info` estimates redemption
without submitting a transaction. Share counts and equity retain the upstream
protobuf byte encoding (`SerializableInt`), rather than decimal text.


## Historical State

Pass gRPC metadata to read application state at a specific block height. Use a
provider that retains the requested state:

```python
from typed_dydx.chain import Chain

metadata = {'x-cosmos-block-height': '100000000'}

async with Chain.kingnodes_archive() as chain:
  subaccount = await chain.subaccounts.subaccount(
    'dydx1...', number=0, metadata=metadata,
  )
  balances = await chain.bank.all_balances_paged(
    'dydx1...', resolve_denom=False, limit=100, metadata=metadata,
  )
```

`metadata` is forwarded to the underlying gRPC call; paged methods forward it on
every page. Keep its values fixed during a walk to query the same historical state
throughout. Omitting it leaves the node's default query behavior unchanged.

Metadata accepts either a mapping or a collection of `(name, value)` pairs;
pairs preserve repeated header names, and values can be strings or bytes for binary
headers. The Cosmos block-height header takes a decimal string. It is separate from
protobuf request fields such as `get_block_by_height`'s `height` parameter.
