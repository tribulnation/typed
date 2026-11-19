# Place & Manage Orders

Trading needs the wallet private key: every order is signed with EIP-712 by the client
(see [Authenticated Setup](../authenticated-setup.md)). You pass the order's terms; the
client adds the chain id, generates an order id and signs. Prices and quantities accept a
`Decimal` or a string.

Before you send an order, know the venue's checks: a notional of at least 5 USD, a limit
price within 5% of the mark price, at most 500 active orders, and 30 "heavy" requests
(order create, cancel and replace, TP/SL changes, position close) per 60 seconds per
account. Processing is asynchronous: an order in status `NEW` has entered the book; follow
its fills through `orders.get` or the [orders stream](listen-to-live-streams.md).

## Place a Limit Order

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  order = await client.exchange.orders.place_limit(
    instrument='BTCUSD', side='BUY', leverage=5, quantity='0.001', limit_price='60000'
  )
  print(order['id'], order['status'])
```

`time_in_force` takes `GTC` (default), `DAY`, `IOC` or `FOK`. `tpsl` attaches
take-profit/stop-loss legs to the order:

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  order = await client.exchange.orders.place_limit(
    instrument='BTCUSD',
    side='BUY',
    leverage=5,
    quantity='0.001',
    limit_price='60000',
    tpsl=[
      {'type': 'take-profit', 'side': 'SELL', 'quantity': '0', 'price': '66000'},
      {'type': 'stop-loss', 'side': 'SELL', 'quantity': '0', 'price': '57000'},
    ],
  )
```

## Place Market and Stop-Limit Orders

A market order is sized in USD (`cash_quantity`) and must be `IOC` or `FOK`:

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  market = await client.exchange.orders.place_market(
    instrument='BTCUSD', side='BUY', leverage=5, cash_quantity='10', time_in_force='IOC'
  )
  stop = await client.exchange.orders.place_stop_limit(
    instrument='BTCUSD',
    side='BUY',
    leverage=5,
    quantity='0.001',
    stop_price='66000',
    limit_price='66100',
  )
```

## Query, Replace and Cancel

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  order = await client.exchange.orders.place_limit(
    instrument='BTCUSD', side='BUY', leverage=5, quantity='0.001', limit_price='60000'
  )
  details = await client.exchange.orders.get(order['id'])
  print(details)

  await client.exchange.orders.replace_limit(order['id'], quantity='0.002', limit_price='60500')
  await client.exchange.orders.cancel(order['id'])
```

`replace_stop_limit(order_id, quantity=..., limit_price=..., stop_price=...)` does the
same for stop-limit orders.

## Batch Orders

Place up to 20 limit orders, or replace up to 50, on one instrument in one request. Each
order is signed on its own and gets its own result.

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  placed = await client.exchange.orders.place_limit_batch(
    'BTCUSD',
    orders=[
      {'instrument': 'BTCUSD', 'side': 'BUY', 'leverage': 5, 'quantity': '0.001', 'limitPrice': '59000'},
      {'instrument': 'BTCUSD', 'side': 'BUY', 'leverage': 5, 'quantity': '0.001', 'limitPrice': '58000'},
    ],
  )
  for result in placed:
    print(result['orderId'], result.get('success'), result.get('failReason'))

  await client.exchange.orders.replace_limit_batch(
    'BTCUSD',
    orders=[{'orderId': placed[0]['orderId'], 'quantity': '0.001', 'limitPrice': '59500'}],
  )
```

## Cancel Many and List Open Orders

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  open_orders = await client.exchange.orders.opened()
  results = await client.exchange.orders.cancel_by_ids([o['id'] for o in open_orders])
  await client.exchange.orders.cancel_by_instrument('BTCUSD')  # everything on one instrument
```

Cancels are not signed, so an API key alone is enough to cancel.
