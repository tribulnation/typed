# Fetch Account Data

Every call on this page works with either an API key or the wallet private key (see
[Authenticated Setup](../authenticated-setup.md)).

## Account

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  me = await client.exchange.account.me()
  print(me.get('exchangeId'), me['wallet'])
```

## Balances and Margin

EVEDEX keeps two balances: the smart-account wallet that deposits land in, and the trading
balance (`funding`) that positions are margined against.

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  margin = await client.exchange.account.available_balance()
  print(margin['availableBalance'], margin['funding']['balance'], margin['negativeUnPnL'])

  for coin in await client.exchange.account.funding():
    print(coin['coin'], coin['quantity'])

  power = await client.exchange.account.power('BTCUSD', leverage=5)
  print(power)
```

`power` is the largest order value you can place on an instrument at a given leverage.

## Positions

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  positions = await client.exchange.positions.list(with_tp_sl='yes')
  for position in positions['list']:
    print(position['instrument'], position['side'], position['quantity'], position['unRealizedPnL'])

  closed = await client.exchange.positions.history(instrument='BTCUSD', limit=20)
  print(closed['count'])
```

## Orders and Fills

```python
from datetime import datetime, timedelta, timezone
from typed_evedex import Evedex

now = datetime.now(timezone.utc)
async with Evedex.new() as client:
  open_orders = await client.exchange.orders.opened()
  history = await client.exchange.orders.list(instrument='BTCUSD', status='FILLED', limit=50)
  fills = await client.exchange.fills(after=now - timedelta(days=7), before=now)
  for fill in fills['list']:
    print(fill)
```

`client.exchange.orders.get(order_id)` and `client.exchange.orders.fills(order_id)` return
one order and its executions.

## Transfers and Balance Ledger

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  transfers = await client.exchange.transfers.list(['done'], limit=20)
  ledger = await client.exchange.account.funding_transfers(['realizedPnl', 'fundingRate'])
  stats = await client.exchange.account.statistics(group='month')
  print(transfers['count'], ledger['count'], stats)
```

`funding_transfers` is the ledger of trading-balance changes: deposits, withdrawals,
realized PnL, fees and funding payments.

## Sub-Accounts

Sub-accounts are separate accounts of the same wallet. Listing them needs the private key
(Auth service); reading one sub-account's state works on the Exchange service.

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  accounts = await client.auth.sub_accounts.list('sub')
  state = await client.exchange.sub_accounts.state('auth-id-of-a-sub-account')
  print(accounts, state)
```
