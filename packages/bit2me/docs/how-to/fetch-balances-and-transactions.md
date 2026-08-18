# Fetch Balances & Transactions

Use `Bit2Me.new()` for authenticated balance and transaction history flows.

## Fetch Trading Balances

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()
  print(balances[0]['currency'], balances[0]['balance'])
```

## Fetch Wallet Transactions

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  transactions = await client.v2.wallet.transactions(limit=20)
  print(transactions['data'][0]['type'])
```

## Fetch Earn Wallets

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  wallets = await client.v2.earn.wallets(limit=20)
  print(wallets['data'][0]['currency'])
```
