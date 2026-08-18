# Place & Manage Orders

Trading calls are signed — see [API Keys Setup](../api-keys.md). Orders execute against real
funds, so start with the venue's minimum order size while testing.

## Place An Order

```python
from binance import Binance

async with Binance.new() as client:
  order = await client.spot.trading.order(
    symbol='BTCUSDT', side='BUY', type='LIMIT',
    time_in_force='GTC', quantity='0.0001', price='20000',
  )
  print(order['orderId'], order['clientOrderId'])
```

`type` decides which other fields are required: `LIMIT` needs `time_in_force`, `quantity`
and `price`; `MARKET` needs `quantity` or `quote_order_qty`; `STOP_LOSS`/`TAKE_PROFIT` need
`quantity` and either `stop_price` or `trailing_delta`. `client.spot.trading.order_test`
validates an order the same way without sending it to the matching engine.

## Query An Order

```python
from binance import Binance

async with Binance.new() as client:
  order = await client.spot.account.order(symbol='BTCUSDT', order_id=123456789)
  print(order['status'])
```

Either `order_id` or `orig_client_order_id` identifies the order.

## Cancel An Order

```python
from binance import Binance

async with Binance.new() as client:
  cancelled = await client.spot.trading.cancel_order(symbol='BTCUSDT', order_id=123456789)
  print(cancelled['status'])
```

## Cancel All Open Orders

```python
from binance import Binance

async with Binance.new() as client:
  cancelled = await client.spot.trading.cancel_open_orders(symbol='BTCUSDT')
```

Cancels every active order on the symbol, including orders that are part of an order list.

## List Open Orders

```python
from binance import Binance

async with Binance.new() as client:
  open_orders = await client.spot.account.open_orders(symbol='BTCUSDT')
```

Omitting `symbol` returns open orders across every symbol, at a much higher request weight.

`client.spot.trading` also has `cancel_replace`, `oco`, and the `order_list_*` family for
multi-leg orders. USD-M futures, COIN-M futures, and options each expose their own `trading`
surface the same way, e.g. `client.usdm_futures.trading`.
