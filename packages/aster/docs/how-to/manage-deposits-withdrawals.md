# Manage Deposits & Withdrawals

Each trading surface has a `wallet` router, and Aster Chain has its own under `client.chain`.
Their reads are signed by your API wallet; the asset lists under `client.bapi` are public. See [Authenticated Setup](../authenticated-setup.md).

## Supported Assets

`client.bapi.wallet` lists every asset that can be deposited or withdrawn, per chain, for the
spot or the perp account. It is public and always answers from mainnet:

```python
from typed_aster import Aster

async with Aster.new(public=True) as client:
  deposits = await client.bapi.wallet.deposit_assets(account_type='perp')
  withdrawals = await client.bapi.wallet.withdraw_assets(chain_ids='56,42161', account_type='spot')
  for asset in deposits:
    print(asset['chainId'], asset['name'], asset['contractAddress'], asset['decimals'])
```

Leave out `chain_ids` to list every chain. Solana assets (`chainId` 101) also carry the
program accounts a deposit goes through, such as `tokenMint`.

## Deposit Addresses

Deposits from EVM chains and Solana go through Aster's deposit contracts, not an API call.
For SUI, fetch your dedicated deposit address:

```python
from typed_aster import Aster

async with Aster.new() as client:
  address = await client.spot.wallet.deposit_address('SUI')
  print(address)
```

## Withdrawal Limits And Fees

```python
from typed_aster import Aster

async with Aster.new() as client:
  limits = await client.futures.wallet.withdraw_info()
  fee = await client.spot.wallet.estimate_withdraw_fee(chain_id='56', asset='USDT')
  print(limits, fee)
```

## Withdraw

An EVM withdrawal is signed twice: your main wallet signs the withdrawal itself, then the API
wallet signs the request. The client needs both keys, and the API wallet needs withdrawal
permission.

```python
from decimal import Decimal

from typed_aster import Aster

async with Aster.new() as client:
  await client.futures.wallet.withdraw(
    amount=Decimal('25'),
    chain_id=56,
    asset='USDT',
    fee=Decimal('0.5'),
    receiver='0x...your-address',
  )
```

`client.spot.wallet.withdraw` and `client.prediction.wallet.withdraw` work the same way.
`solana_withdraw` sends to a Solana address and is signed by the API wallet alone.

## Move Funds Between Wallets

```python
from decimal import Decimal

from typed_aster import Aster

async with Aster.new() as client:
  await client.futures.wallet.transfer(
    Decimal('10'), asset='USDT', client_tran_id='move-1', kind_type='FUTURE_SPOT'
  )
```

## History

```python
from typed_aster import Aster

async with Aster.new() as client:
  history = await client.futures.wallet.deposit_withdraw_history()
  print(history)
```

## On Aster Chain

On mainnet, `client.chain.perp` and `client.chain.spot` offer the same withdrawals,
transfers and history against your Aster Chain accounts, and `client.chain.account.transfer`
sends an asset to another Aster Chain address. Aster Chain transfers are signed by the main
wallet.
