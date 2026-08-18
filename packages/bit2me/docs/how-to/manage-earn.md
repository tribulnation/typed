# Query & Manage Earn

## Browse Earn Assets And Yields

Public: use `Bit2Me.public()`:

```python
from bit2me import Bit2Me

async with Bit2Me.public() as client:
  apy = await client.v2.earn.apy()          # annual percentage yield per currency
  assets = await client.v2.earn.assets()    # every currency Earn currently supports
  print(list(apy.keys())[:3], assets[0].get('currency'))
```

## Your Earn Wallets

```python
from dotenv import load_dotenv
from bit2me import Bit2Me

load_dotenv()

async with Bit2Me.new() as client:
  wallets = await client.v2.earn.wallets(limit=20)
  data = wallets.get('data', [])
  if data:
    print(data[0].get('currency'), data[0].get('balance'))
```

`v1.earn.wallets.get(wallet_id)` fetches one wallet's full detail, and `v1.earn.wallets.list_movements(wallet_id)` its deposit/withdrawal/reward history.

## Deposit And Withdraw From Earn

```python
from dotenv import load_dotenv
from bit2me import Bit2Me

load_dotenv()

async with Bit2Me.new() as client:
  deposit = await client.v1.earn.movements.create({    # move funds into Earn
    'currency': 'BTC',
    'amount': '0.001',
    'type': 'deposit',
  })
  print(deposit['movementId'])
```

Pass `type='withdrawal'` to move funds back out. `movementId` identifies the Earn movement; `walletMovementId` is the matching entry on the wallet's own ledger.
