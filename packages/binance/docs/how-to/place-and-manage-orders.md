# Place & Manage Orders

Trading calls are signed — see [API Keys Setup](../api-keys.md). Orders execute against real
funds, so start with the venue's minimum order size while testing.

## Place An Order

```python
from typed_binance import Binance

async with Binance.new() as client:
  order = await client.spot.http.trading.order({
    'symbol': 'BTCUSDT', 'side': 'BUY', 'type': 'LIMIT',
    'timeInForce': 'GTC', 'quantity': '0.0001', 'price': '20000',
  })
  print(order['orderId'], order['clientOrderId'])
```

The request body is a `LimitOrder | MarketOrder | StopLossOrder | StopLossLimitOrder |
TakeProfitOrder | TakeProfitLimitOrder | LimitMakerOrder` union — `type` decides which
variant, and each variant's own required fields differ: `LIMIT` needs `timeInForce`,
`quantity` and `price`; `MARKET` needs `quantity` or `quoteOrderQty`; `STOP_LOSS`/
`TAKE_PROFIT` need `quantity` and either `stopPrice` or `trailingDelta`.
`client.spot.http.trading.order_test` validates an order the same way without sending it to the
matching engine.

## Query An Order

```python
from typed_binance import Binance

async with Binance.new() as client:
  order = await client.spot.http.account.order(symbol='BTCUSDT', order_id=123456789)
  print(order['status'])
```

Either `order_id` or `orig_client_order_id` identifies the order.

## Cancel An Order

```python
from typed_binance import Binance

async with Binance.new() as client:
  cancelled = await client.spot.http.trading.cancel_order(symbol='BTCUSDT', order_id=123456789)
  print(cancelled['status'])
```

## Cancel All Open Orders

```python
from typed_binance import Binance

async with Binance.new() as client:
  cancelled = await client.spot.http.trading.cancel_open_orders(symbol='BTCUSDT')
```

Cancels every active order on the symbol, including orders that are part of an order list.

## List Open Orders

```python
from typed_binance import Binance

async with Binance.new() as client:
  open_orders = await client.spot.http.account.open_orders(symbol='BTCUSDT')
```

Omitting `symbol` returns open orders across every symbol, at a much higher request weight.

`client.spot.http.trading` also has `cancel_replace`, `oco`, and the `order_list_*` family for
multi-leg orders. USD-M futures, COIN-M futures, and options each expose their own `trading`
surface the same way, e.g. `client.usdm_futures.http.trading`.
