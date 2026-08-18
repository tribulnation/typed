# Manage Deposits & Withdrawals

All of these are authenticated.

## Deposit Address

```python
from bitget import Bitget

async with Bitget.new() as client:
  address = await client.uta.transfers.deposit_address(coin='USDT', chain='TRC20')
```

## Deposit Records

```python
from bitget import Bitget

async with Bitget.new() as client:
  deposits = await client.uta.transfers.deposit_records(
    start_time=1700000000000, end_time=1700086400000,
  )
```

## Withdraw

```python
from bitget import Bitget

async with Bitget.new() as client:
  result = await client.uta.transfers.withdraw({
    'coin': 'USDT',
    'chain': 'TRC20',
    'transferType': 'on_chain',
    'address': 'your_destination_address',
    'size': '10',
  })
```

`transferType` is `on_chain` for an external withdrawal or `internal_transfer` to send directly
to another Bitget user.

## Withdrawal Records

```python
from bitget import Bitget

async with Bitget.new() as client:
  withdrawals = await client.uta.transfers.withdraw_records(
    start_time=1700000000000, end_time=1700086400000,
  )
```

## Internal Transfers Between Account Types

```python
from bitget import Bitget

async with Bitget.new() as client:
  await client.uta.transfers.transfer({
    'fromType': 'spot',
    'toType': 'uta',
    'coin': 'USDT',
    'amount': '10',
  })
```

## Classic v2

```python
from bitget import Bitget

async with Bitget.new() as client:
  address = await client.classic.spot.deposit_address(coin='USDT', chain='TRC20', size='')
  await client.classic.spot.withdraw({
    'coin': 'USDT', 'transferType': 'on_chain', 'address': 'your_destination_address', 'size': '10',
  })
```
