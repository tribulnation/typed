# Place & Manage Orders

`trading` needs credentials — see [API Keys Setup](../api-keys.md). Every example below
targets `testnet=True`; run write calls against testnet only.

## Place An Order

`buy`/`sell` take one positional argument, a discriminated union keyed by `type`
(`limit`, `market`, `stop_limit`, ...):

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  order = await client.http.trading.buy({
    'instrument_name': 'BTC-PERPETUAL',
    'amount': 10,
    'type': 'limit',
    'price': 32503.0,
  })
  print(order['order']['order_id'], order['order']['order_state'])
```

## Inspect Open Orders

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  orders = await client.http.trading.get_open_orders_by_instrument(
    instrument_name='BTC-PERPETUAL',
  )
  for order in orders:
    print(order['order_id'], order['direction'], order['price'])
```

## Query An Order

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  order = await client.http.trading.get_order_state(order_id='some-order-id')
  print(order['order_state'], order.get('filled_amount'))
```

## Cancel An Order

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  cancelled = await client.http.trading.cancel(order_id='some-order-id')
  print(cancelled['order_state'])
```

## Cancel All Orders

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  count = await client.http.trading.cancel_all()
  print(count)
```

`cancel_all_by_instrument` and `cancel_all_by_currency` narrow the same bulk cancel to one
instrument or currency instead of every open order.
