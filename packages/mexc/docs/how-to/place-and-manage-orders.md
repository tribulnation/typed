# Place & Manage Orders

Spot trading methods live on `client.spot.http.trade`, futures on `client.futures.http.trade`.

For safe live testing, `USDCUSDT` is a practical symbol because you can buy a very small amount.

## Place A Spot Market Order

```python
from decimal import Decimal
from typed_mexc import MEXC

async with MEXC.new() as client:
  order = await client.spot.http.trade.place_order({
    'symbol': 'USDCUSDT',
    'side': 'BUY',
    'type': 'MARKET',
    'quantity': Decimal('1'),
  })
  print(order['orderId'])
```

## Query A Spot Order

```python
from typed_mexc import MEXC

order_id = 'your-order-id'

async with MEXC.new() as client:
  order = await client.spot.http.account.order(symbol='USDCUSDT', order_id=order_id)
  print(order['status'])
```

## Fetch Open Spot Orders

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  orders = await client.spot.http.account.open_orders(symbol='USDCUSDT')
  print(len(orders))
```

## Fetch Spot Order History

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  orders = await client.spot.http.account.orders(symbol='USDCUSDT', limit=20)
  print(orders[0]['orderId'])
```

## Place A Cancelable Spot Limit Order

Use a far-off limit price with valid notional if you want an order that stays open long enough to cancel.

```python
from decimal import Decimal
from typed_mexc import MEXC

async with MEXC.new() as client:
  order = await client.spot.http.trade.place_order({
    'symbol': 'USDCUSDT',
    'side': 'BUY',
    'type': 'LIMIT',
    'price': Decimal('0.8000'),
    'quantity': Decimal('2'),
  })
  print(order['orderId'])
```

## Cancel A Spot Order

```python
from typed_mexc import MEXC

order_id = 'your-order-id'

async with MEXC.new() as client:
  order = await client.spot.http.trade.cancel_order(symbol='USDCUSDT', order_id=order_id)
  print(order['status'])
```

## Cancel All Spot Orders For A Symbol

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  orders = await client.spot.http.trade.cancel_open_orders(symbol='USDCUSDT')
  print(len(orders))
```

## Place A Futures Order

Futures side and type are numeric codes: `side=1` opens a long, `type=1` is a limit order.

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  order = await client.futures.http.trade.submit_order({
    'symbol': 'BTC_USDT',
    'price': 10000,
    'vol': 1,
    'side': 1,
    'type': 1,
    'openType': 2,
  })
  if 'data' in order:
    print(order['data'])
```

## Query A Futures Order

```python
from typed_mexc import MEXC

order_id = 'your-order-id'

async with MEXC.new() as client:
  order = await client.futures.http.trade.order(order_id)
  if 'data' in order:
    print(order['data']['state'])
```

## Fetch Open Futures Orders

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  orders = await client.futures.http.trade.open_orders('BTC_USDT', page_num=1, page_size=20)
  if 'data' in orders:
    print(len(orders['data']))
```

## Cancel A Futures Order

```python
from typed_mexc import MEXC

order_id = 'your-order-id'

async with MEXC.new() as client:
  result = await client.futures.http.trade.cancel_order([order_id])
  if 'data' in result:
    print(result['data'][0]['errorCode'])
```

## Cancel All Futures Orders For A Symbol

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  await client.futures.http.trade.cancel_all_orders('BTC_USDT')
```
