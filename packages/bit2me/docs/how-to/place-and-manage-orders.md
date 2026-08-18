# Place & Manage Orders

Use the authenticated router:

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  ...
```

## Place An Order

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  order = await client.v1.trading.orders.create({
    'side': 'buy',
    'symbol': 'BTC/EUR',
    'price': '50000',
    'amount': '0.001',
    'orderType': 'limit',
    'timeInForce': 'GTC',
  })
  print(order['id'])
```

## List Orders

```python
from bit2me import Bit2Me

async with Bit2Me.new() as client:
  orders = await client.v1.trading.orders.list(
    symbol='BTC/EUR',
    limit=20,
    status='open',
  )
  print(len(orders))
```

## Get A Specific Order

```python
from bit2me import Bit2Me

order_id = 'your-order-id'

async with Bit2Me.new() as client:
  order = await client.v1.trading.orders.get(order_id)
  print(order['status'])
```

## List Trades For An Order

```python
from bit2me import Bit2Me

order_id = 'your-order-id'

async with Bit2Me.new() as client:
  trades = await client.v1.trading.orders.list_trades(order_id)
  print(trades[0]['price'])
```

## Cancel An Order

```python
from bit2me import Bit2Me

order_id = 'your-order-id'

async with Bit2Me.new() as client:
  order = await client.v1.trading.orders.cancel(order_id)
  print(order['status'])
```
