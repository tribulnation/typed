# Place And Manage Orders

`client.http.trade` places, amends, and cancels orders. It needs credentials — see
[API Keys Setup](../api-keys.md).

## Placing An Order

`create_order` takes a single `CreateOrderRequest` dict, not keyword arguments. Required
keys are `category`, `symbol`, `side`, `orderType`, and `qty`; a limit order also needs
`price`:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  order = await client.http.trade.create_order({
    'category': 'spot', 'symbol': 'BTCUSDT',
    'side': 'Buy', 'orderType': 'Limit', 'qty': '0.001', 'price': '20000',
  })
  print(order['orderId'], order['orderLinkId'])
```

`timeInForce` accepts `'GTC'`, `'IOC'`, `'FOK'`, `'PostOnly'`, or `'RPI'`, and defaults to
`GTC` (market orders always use `IOC`). `orderLinkId` sets your own order identifier.
`takeProfit`/`stopLoss` attach exit orders at creation time, and `reduceOnly` restricts the
order to shrinking an existing position. The response only acknowledges that Bybit accepted
the request — placement is asynchronous, so the order may not be live yet.

## Amending An Order

`amend_order` takes an `AmendOrderRequest` dict. `category` and `symbol` are required,
plus one of `orderId`/`orderLinkId` to target the order. Every other key is optional —
whatever you omit is left unchanged:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  order = await client.http.trade.create_order({
    'category': 'spot', 'symbol': 'BTCUSDT',
    'side': 'Buy', 'orderType': 'Limit', 'qty': '0.001', 'price': '20000',
  })
  amended = await client.http.trade.amend_order({
    'category': 'spot', 'symbol': 'BTCUSDT',
    'orderId': order['orderId'], 'qty': '0.002', 'price': '19500',
  })
```

## Cancelling An Order

`cancel_order` takes a `CancelOrderRequest` dict: `category`, `symbol`, and one of
`orderId`/`orderLinkId`:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  order = await client.http.trade.create_order({
    'category': 'spot', 'symbol': 'BTCUSDT',
    'side': 'Buy', 'orderType': 'Limit', 'qty': '0.001', 'price': '20000',
  })
  cancelled = await client.http.trade.cancel_order({
    'category': 'spot', 'symbol': 'BTCUSDT', 'orderId': order['orderId'],
  })
```

## Cancelling All Orders

`cancel_all_orders` takes a `CancelAllOrdersRequest` dict. `category` is required; spot
needs no further scoping, while linear/inverse need one of `symbol`, `baseCoin`, or
`settleCoin`:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  result = await client.http.trade.cancel_all_orders({
    'category': 'linear', 'settleCoin': 'USDT',
  })
  for cancelled in result['list']:
    print(cancelled['orderId'])
```

## Batch Requests

`batch_place_order`, `batch_amend_order`, and `batch_cancel_order` submit up to several
orders in a single call, each taking a list of the same per-order fields shown above.

## Listing Open Orders

`open_orders` takes keyword arguments only. `category` is required; the rest scope and
page the result:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  page = await client.http.trade.open_orders(category='spot', symbol='BTCUSDT', limit=50)
  for o in page['list']:
    print(o['orderId'], o['orderStatus'])
```

`open_orders` also returns the most recent 500 closed orders when `open_only=1` is passed.
It has a `open_orders_paged` iterator for walking every page automatically — see
[Paginate Through Results](paginate-through-results.md).

## Order History

`order_history` has the same keyword shape as `open_orders`, but queries closed, filled,
and cancelled orders beyond the 500-record realtime window `open_orders` covers:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  page = await client.http.trade.order_history(category='spot', symbol='BTCUSDT', limit=50)
  for o in page['list']:
    print(o['orderId'], o['orderStatus'], o['updatedTime'])
```

It also has an `order_history_paged` iterator; see
[Paginate Through Results](paginate-through-results.md).

## Order Entry Over WebSocket

For order-entry over WebSocket instead of REST, see
[Async Usage](../reference/async-usage.md#the-ws-trade-connection).
