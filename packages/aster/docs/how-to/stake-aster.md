# Stake ASTER

Staking lives on Aster Chain, under `client.chain.staking`. Aster Chain runs on mainnet only.
Reads are signed by your API wallet; staking changes are signed by your main wallet, so the
client needs `main` or `ASTER_USER_PRIVATE_KEY`. See [Authenticated Setup](../authenticated-setup.md).

## Check Your Position

```python
from typed_aster import Aster

async with Aster.new() as client:
  status = await client.chain.staking.stake_account_status()
  position = await client.chain.staking.my_staking()
  rewards = await client.chain.staking.claimable_rewards()
  print(status, position, rewards)
```

The network-wide total needs no credentials:

```python
from typed_aster import Aster

async with Aster.new(public=True) as client:
  print(await client.chain.staking.locked_aster())
```

## Stake

Create a position by delegating ASTER to a validator for a lock period, then add to it:

```python
from decimal import Decimal

from typed_aster import Aster

async with Aster.new() as client:
  validator = '0x...validator-address'
  await client.chain.staking.create(
    validator, stake_amount=Decimal('100'), period_code='52_WEEKS'
  )
  await client.chain.staking.deposit(validator, stake_amount=Decimal('50'))
```

## Extend And Claim

```python
from decimal import Decimal

from typed_aster import Aster

async with Aster.new() as client:
  await client.chain.staking.update_lock_period('104_WEEKS')
  await client.chain.staking.claim_rewards(Decimal('1.5'))
```
