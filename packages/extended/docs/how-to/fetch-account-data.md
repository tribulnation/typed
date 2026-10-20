# Fetch Account Data

Every `client.account` call reads the sub-account the API key belongs to, so an API key alone
is enough (see [Authenticated Setup](../authenticated-setup.md)).

## Account And Sub-Accounts

```python
from typed_extended import Extended

async with Extended.new() as client:
  info = await client.account.info()
  print(info['accountId'], info['status'])
  for sub in await client.account.sub_accounts():
    print(sub['accountId'], sub['accountIndex'], sub.get('description'))
```

## Balance

```python
from typed_extended import Extended

async with Extended.new() as client:
  balance = await client.account.balance()
  print(
    balance['equity'], balance['availableForTrade'], balance['availableForWithdrawal']
  )
  print(balance['unrealisedPnl'], balance['marginRatio'], balance['leverage'])
  spot = await client.account.spot_balances()
```

## Positions

```python
from typed_extended import Extended

async with Extended.new() as client:
  positions = await client.account.positions(['BTC-USD'])
  for position in positions:
    print(
      position['market'],
      position['side'],
      position['size'],
      position['openPrice'],
      position['unrealisedPnl'],
    )
```

## Trades, Orders And Funding History

Each history call returns one page: `data` plus a `pagination` cursor.

```python
from datetime import datetime, timezone
from typed_extended import Extended

async with Extended.new() as client:
  trades = await client.account.trades(['BTC-USD'], limit=50)
  for trade in trades['data']:
    print(
      trade['createdTime'], trade['side'], trade['price'], trade['qty'], trade['fee']
    )
  orders = await client.account.orders_history(market=['BTC-USD'], limit=50)
  funding = await client.account.funding_history(
    market=['BTC-USD'],
    start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
    limit=50,
  )
  closed = await client.account.positions_history(['BTC-USD'], limit=50)
```

To walk every page, use the `_paged` variants in
[Paginate Through Results](paginate-through-results.md).

## Fees

```python
from typed_extended import Extended

async with Extended.new() as client:
  for fee in await client.account.fees(['BTC-USD']):
    print(fee['market'], fee['makerFeeRate'], fee['takerFeeRate'])
```

## Portfolio Analytics

`client.portfolio` charts equity, PnL, drawdown, funding and health by account id. Only the
API key's own account is accepted: asking for another sub-account of the same wallet raises
`AuthError` (HTTP `403`).

```python
from typed_extended import Extended

async with Extended.new() as client:
  info = await client.account.info()
  health = await client.portfolio.health([info['accountId']])
  print(health)
```
