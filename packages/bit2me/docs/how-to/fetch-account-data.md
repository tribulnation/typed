# Fetch Account Data

All of these need credentials, so use `Bit2Me.new()`.

## Trading Balance And Working Capital

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  balances = await client.v1.trading.balance()             # per-currency trading balances
  working_capital = await client.v1.trading.working_capital()  # working-capital limits & usage
  print(balances[0].get('currency'), balances[0].get('balance'))
```

## Trade And Funding History

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  trades = await client.v1.trading.trades.list(symbol='BTC/EUR', limit=20)   # your fills
  funding = await client.v1.trading.funding_movements(limit=20)              # trading deposits/withdrawals
  print(trades.get('total'), funding[:1])
```

## Wallet Pockets And Transactions

Pockets are the Bit2Me Wallet's per-currency sub-balances; trading balance (above) is a separate, Pro-account balance:

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  pockets = await client.v1.wallet.pockets.get()               # every wallet pocket
  transactions = await client.v2.wallet.transactions(limit=20)  # wallet transaction history
  print(pockets[0]['name'], pockets[0]['balance'])
  print(transactions.get('data', [])[:1])
```

## Earn Balances

`v1.earn.summary` gives one converted total across every Earn wallet. See [Query & Manage Earn](manage-earn.md) for per-wallet detail.

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  summary = await client.v1.earn.summary(user_currency='EUR')
  print(summary['totalBalance'], summary['totalRewards'])
```
