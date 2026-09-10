# Manage Deposits & Withdrawals

Deposit and withdrawal methods live on `client.spot.http.wallet`.

## Fetch A Deposit Address

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  addresses = await client.spot.http.wallet.deposit_address(coin='USDT')
  print(addresses[0]['address'], addresses[0]['network'])
```

## Generate A New Deposit Address

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  addresses = await client.spot.http.wallet.generate_deposit_address(coin='USDT', network='TRC20')
  print(addresses[0]['address'])
```

## Fetch Deposit History

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  deposits = await client.spot.http.wallet.deposit_history(coin='USDT', limit=20)
  print(deposits[0]['amount'] if deposits else None)
```

## Submit A Withdrawal

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  result = await client.spot.http.wallet.withdraw(
    coin='USDT',
    address='your-destination-address',
    amount='1',
  )
  print(result['id'])
```

## Fetch Withdrawal History

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  withdrawals = await client.spot.http.wallet.withdraw_history(coin='USDT', limit=20)
  print(withdrawals[0]['status'] if withdrawals else None)
```

## Cancel A Withdrawal

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  result = await client.spot.http.wallet.cancel_withdraw(id='your-withdrawal-id')
  print(result['id'])
```
