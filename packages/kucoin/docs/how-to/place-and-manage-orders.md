# Place & Manage Orders

Spot trading goes through the high-frequency (`hf`) order book, which matches through a
dedicated engine with lower latency than the plain order book. These calls need a key
with `Trade` permission — see [API Keys Setup](../api-keys.md).

## Place a Limit Order

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  result = await client.spot.orders_hf.add({
    'symbol': 'BTC-USDT',
    'type': 'limit',
    'side': 'buy',
    'price': '10000',
    'size': '0.0001',
  })
  print(result['orderId'])
```

A market order takes `size` (base currency) or `funds` (quote currency) instead of
`price`:

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  result = await client.spot.orders_hf.add({
    'symbol': 'BTC-USDT', 'type': 'market', 'side': 'buy', 'funds': '10',
  })
```

## Query an Order

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  order = await client.spot.orders_hf.get_by_order_id('order-id', symbol='BTC-USDT')
  print(order['id'], order['active'])
```

## List Open Orders

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  open_orders = await client.spot.orders_hf.get_open_orders(symbol='BTC-USDT')
  for order in open_orders or []:
    print(order['id'], order['side'], order['price'])
```

## Cancel an Order

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  cancelled = await client.spot.orders_hf.cancel_by_order_id(
    'order-id', symbol='BTC-USDT',
  )
  print(cancelled['orderId'])
```

Cancellation is a request, not a guarantee — confirm with `get_by_order_id` or the
private order WebSocket topic (see [Listen To Streams](listen-to-streams.md)).

## Cancel All Orders

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  result = await client.spot.orders_hf.cancel_all()
  print(result['succeedSymbols'], result['failedSymbols'])
```

## Stop and OCO Orders

`spot.stop_orders` and `spot.oco_orders` expose the same add/get/cancel shape for
stop-loss and one-cancels-the-other orders. `margin.orders_hf` and `futures.orders`
expose the equivalent surface for Margin and Futures.
