# Query & Manage Deposits/Withdrawals

All of these need credentials, so use `Bit2Me.new()`.

## Manage Wallet Pockets

Pockets are the Bit2Me Wallet's per-currency sub-balances:

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  pocket = await client.v1.wallet.pockets.create({'currency': 'BTC', 'name': 'Savings'})  # create a pocket
  await client.v1.wallet.pockets.update({'id': pocket['id'], 'name': 'Renamed'})          # rename it
  await client.v1.wallet.pockets.delete(id=pocket['id'])                                  # delete it
```

## Find A Deposit Address

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  pockets = await client.v1.wallet.pockets.get()
  addresses = await client.v2.wallet.pockets(pockets[0]['id'], 'bitcoin')  # find-or-create address
  print(addresses[0].get('address'), addresses[0].get('network'))
```

## Move Funds Between Wallet And Trading

Trading balance (see [Fetch Account Data](fetch-account-data.md)) is a separate, Pro-account balance funded from a wallet pocket:

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  pockets = await client.v1.wallet.pockets.get()
  deposit = await client.v1.trading.wallets.request_deposit({     # wallet -> trading
    'fromPocketId': pockets[0]['id'],
    'amount': '100',
    'currency': 'EUR',
  })
  withdrawal = await client.v1.trading.wallets.request_withdrawal({  # trading -> wallet
    'toPocketId': pockets[0]['id'],
    'amount': '0.001',
    'currency': 'BTC',
  })
  print(deposit.get('balance'), withdrawal.get('balance'))
```

## Withdraw To A Blockchain Address

A wallet withdrawal is a two-step proforma/execute flow, same as any other wallet transaction. Check the proforma's `fee`/`expirationTime` before executing:

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  pockets = await client.v1.wallet.pockets.get()
  proforma = await client.v1.wallet.transactions.preview({
    'pocket': pockets[0]['id'],
    'amount': '0.001',
    'currency': 'BTC',
    'destination': {'address': 'bc1q...', 'network': 'bitcoin'},
  })
  executed = await client.v1.wallet.transactions.execute({'proforma': proforma['id']})
  print(executed['id'])
```
