# Place & Manage Orders

Spot trading methods live on `client.spot.trade`, futures on `client.futures.trade`.

For safe live testing, `USDCUSDT` is a practical symbol because you can buy a very small amount.

## Place A Spot Market Order

```python
from mexc import MEXC

async with MEXC.new() as client:
  order = await client.spot.trade.place_order(
    symbol='USDCUSDT',
    side='BUY',
    type_='MARKET',
    quantity='1',
  )
  print(order['orderId'])
```

## Query A Spot Order

```python
from mexc import MEXC

order_id = 'your-order-id'

async with MEXC.new() as client:
  order = await client.spot.account.order(symbol='USDCUSDT', order_id=order_id)
  print(order['status'])
```

## Fetch Open Spot Orders

```python
from mexc import MEXC

async with MEXC.new() as client:
  orders = await client.spot.account.open_orders(symbol='USDCUSDT')
  print(len(orders))
```

## Fetch Spot Order History

```python
from mexc import MEXC

async with MEXC.new() as client:
  orders = await client.spot.account.orders(symbol='USDCUSDT', limit=20)
  print(orders[0]['orderId'])
```

## Place A Cancelable Spot Limit Order

Use a far-off limit price with valid notional if you want an order that stays open long enough to cancel.

```python
from mexc import MEXC

async with MEXC.new() as client:
  order = await client.spot.trade.place_order(
    symbol='USDCUSDT',
    side='BUY',
    type_='LIMIT',
    price='0.8000',
    quantity='2',
  )
  print(order['orderId'])
```

## Cancel A Spot Order

```python
from mexc import MEXC

order_id = 'your-order-id'

async with MEXC.new() as client:
  order = await client.spot.trade.cancel_order(symbol='USDCUSDT', order_id=order_id)
  print(order['status'])
```

## Cancel All Spot Orders For A Symbol

```python
from mexc import MEXC

async with MEXC.new() as client:
  orders = await client.spot.trade.cancel_open_orders(symbol='USDCUSDT')
  print(len(orders))
```

## Place A Futures Order

Futures side and type are numeric codes: `side=1` opens a long, `type=1` is a limit order.

```python
from mexc import MEXC

async with MEXC.new() as client:
  order = await client.futures.trade.submit_order({
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
from mexc import MEXC

order_id = 'your-order-id'

async with MEXC.new() as client:
  order = await client.futures.trade.order(order_id)
  if 'data' in order:
    print(order['data']['state'])
```

## Fetch Open Futures Orders

```python
from mexc import MEXC

async with MEXC.new() as client:
  orders = await client.futures.trade.open_orders('BTC_USDT', page_num=1, page_size=20)
  if 'data' in orders:
    print(len(orders['data']))
```

## Cancel A Futures Order

```python
from mexc import MEXC

order_id = 'your-order-id'

async with MEXC.new() as client:
  result = await client.futures.trade.cancel_order([order_id])
  if 'data' in result:
    print(result['data'][0]['errorCode'])
```

## Cancel All Futures Orders For A Symbol

```python
from mexc import MEXC

async with MEXC.new() as client:
  await client.futures.trade.cancel_all_orders({'symbol': 'BTC_USDT'})
```
