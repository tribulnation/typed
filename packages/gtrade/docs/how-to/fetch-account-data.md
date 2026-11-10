# Fetch Account Data

The Trading API's account reads need an agent key or a read-only API key (see
[Wallet & Agent Setup](../authenticated-setup.md)). Every read takes the trader (master
wallet) address, and it must be the trader the credential belongs to: another address
raises `AuthError` (`TRADER_MISMATCH`).

## Balances & Agents

```python
from typed_gtrade import GTrade

trader = '0x...'  # the trader (master wallet) address

async with GTrade.new() as client:
  account = await client.trading.account.get(trader)
  for balance in account['balances']:
    print(balance['collateral'], balance['balance'], balance['allowance'])
  print([(a['agent'], a['status']) for a in account['agents']])
```

`allowance` is what the trader has approved the Diamond to spend: an order needs it to
cover the collateral.

## Positions

```python
from typed_gtrade import GTrade

trader = '0x...'

async with GTrade.new() as client:
  for position in await client.trading.account.positions(trader):
    print(position['id'], position['market'], position['side'], position['size'])
    print(position['entryPrice'], position['markPrice'], position['liquidationPrice'], position['unrealizedPnl'])
```

Positions are isolated margin. PnL and fees are in the collateral token.

## Open Orders & One Order

```python
from typed_gtrade import GTrade

trader = '0x...'

async with GTrade.new() as client:
  orders = await client.trading.account.orders(trader)
  for order in orders:
    print(order['id'], order['market'], order['type'], order['status'], order['price'])
  if orders:
    order = await client.trading.orders.get(orders[0]['id'])
```

`account.orders` lists resting limit/stop orders and market orders awaiting execution.

## Order History & Fills

```python
from typed_gtrade import GTrade

trader = '0x...'

async with GTrade.new() as client:
  history = await client.trading.account.order_history(address=trader, limit=100)
  fills = await client.trading.account.fills(address=trader, limit=100)
  print(len(history['data']), history['nextCursor'])
  for fill in fills['data']:
    print(fill['market'], fill['action'], fill['price'], fill['pnl'], fill['timestamp'])
```

Both are newest first, up to 500 rows per page. Order history only covers orders placed
through the Trading API. To walk every page, see
[Paginate Through Results](paginate-through-results.md).

## Any Trader, Without Credentials

The backends expose every trader's on-chain state and history publicly:

```python
from typed_gtrade import GTrade

trader = '0x...'

async with GTrade.new(public=True) as client:
  open_trades = await client.backend.trades.by_trader(trader)
  stats = await client.backend_global.traders.stats(trader, chain_id=42161)
  history = await client.backend_global.traders.history(address=trader, chain_id=42161, limit=50)
  print(len(open_trades), stats['totalTrades'], [row['action'] for row in history['data']])
```

Backend trades are raw contract-precision integers; Backend Global values are floats (see
[Numbers & Precision](../reference/numbers.md)). `traders.batch_history` and
`traders.batch_stats` read up to 50 addresses at once.
