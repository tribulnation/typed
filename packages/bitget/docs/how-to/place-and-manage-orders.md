# Place & Manage Orders

All of these are authenticated.

## Place An Order

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  order = await client.uta.trade.place_order({
    'category': 'SPOT',
    'symbol': 'BTCUSDT',
    'side': 'buy',
    'orderType': 'limit',
    'qty': '0.001',
    'price': '20000',
    'timeInForce': 'gtc',
  })
```

`category` is one of `SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`. Futures
orders additionally take `posSide` (`long`/`short`, required in hedge mode), `marginMode`
(`crossed`/`isolated`), and `reduceOnly`.

## Look Up An Order

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  info = await client.uta.trade.order_info(order_id='your_order_id')
```

Lookups, cancels, and modifies all accept either `order_id` or `client_oid`. Pass whichever
you tracked the order by.

## Cancel An Order

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  await client.uta.trade.cancel_order({'orderId': 'your_order_id', 'category': 'SPOT'})
```

## List Open Orders

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  open_orders = await client.uta.trade.unfilled_orders(category='SPOT')
  for o in open_orders['list'] or []:
    print(o['orderId'], o['orderStatus'])
```

## Order History & Fills

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  history = await client.uta.trade.history_orders(category='SPOT', symbol='BTCUSDT')
  fills = await client.uta.trade.fills(category='SPOT')
```

Both are paged, see [Paginate Through Results](paginate-through-results.md).

## Classic v2

```python
from typed_bitget import Bitget

async with Bitget.new() as client:
  order = await client.classic.spot.place_order({
    'symbol': 'BTCUSDT', 'side': 'buy', 'orderType': 'limit',
    'force': 'gtc', 'price': '20000', 'size': '0.001',
  })
```
