# Move Funds & Pockets

Bit2Me exposes both wallet pocket management and transfers between Bit2Me Wallet and Trading.

## List Wallet Pockets

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  pockets = await client.v1.wallet.pockets.get()
  print(pockets[0]['name'])
```

## Create A Pocket

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  pocket = await client.v1.wallet.pockets.create({
    'currency': 'BTC',
    'name': 'Trading Buffer',
  })
  print(pocket['id'])
```

## Update Or Delete A Pocket

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  await client.v1.wallet.pockets.update({
    'id': 'your-pocket-id',
    'name': 'Renamed Pocket',
  })
  await client.v1.wallet.pockets.delete(id='your-pocket-id')
```

## Find Deposit Addresses For A Pocket

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  addresses = await client.v2.wallet.pockets('your-pocket-id', 'BTC')
  print(addresses[0]['address'])
```

## Move Funds Into Trading

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  wallet = await client.v1.trading.wallets.request_deposit({
    'fromPocketId': 'your-pocket-id',
    'amount': '100',
    'currency': 'EUR',
  })
  print(wallet['balance'])
```

## Move Funds Back Out Of Trading

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  wallet = await client.v1.trading.wallets.request_withdrawal({
    'toPocketId': 'your-pocket-id',
    'amount': '0.001',
    'currency': 'BTC',
  })
  print(wallet['balance'])
```

## Preview And Execute A Wallet Transaction

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  proforma = await client.v1.wallet.transactions.preview({
    'operation': 'buy',
    'pair': 'BTC/EUR',
    'amount': '100',
    'currency': 'EUR',
  })
  executed = await client.v1.wallet.transactions.execute({
    'proforma': proforma['id'],
  })
  print(executed['id'])
```

Some withdrawal-style wallet flows may require additional verification outside plain API-key auth.
