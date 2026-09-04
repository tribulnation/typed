# Place & Manage Orders

Every order call is against Advanced Trade (v3) and requires a CDP API Key — see [API Keys Setup](../api-keys.md).

## Create an Order

`order_configuration` is a discriminated union — pick exactly one key matching the order type:

```python
from decimal import Decimal

from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  market_order = await client.app.advanced_trade.http.orders.create(
    client_order_id='my-market-order-001',
    product_id='BTC-USD',
    side='BUY',
    order_configuration={'market_market_ioc': {'quote_size': Decimal('10')}},
  )
  print(market_order['success'])

  limit_order = await client.app.advanced_trade.http.orders.create(
    client_order_id='my-limit-order-001',
    product_id='BTC-USD',
    side='BUY',
    order_configuration={
      'limit_limit_gtc': {'base_size': Decimal('0.001'), 'limit_price': Decimal('50000.00')},
    },
  )
  print(limit_order['success'])
```

`order_configuration` also accepts `limit_limit_gtd`, `limit_limit_fok`, `stop_limit_stop_limit_gtc`/`_gtd`, `trigger_bracket_gtc`/`_gtd`, `twap_limit_gtd`, `scaled_limit_gtc`, and `sor_limit_ioc` — each variant's own required fields are typed.

## Get, List & Cancel

```python
from decimal import Decimal

from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  order = await client.app.advanced_trade.http.orders.historical.get(order_id='order-id')             # one order by id
  open_orders = await client.app.advanced_trade.http.orders.historical.batch(order_status=['OPEN'])   # open orders
  fills = await client.app.advanced_trade.http.orders.historical.fills(order_ids=['order-id'])        # its fills

  await client.app.advanced_trade.http.orders.edit(
    order_id='order-id', price=Decimal('51000.00'), size=Decimal('0.001'),
  )  # edit in place
  await client.app.advanced_trade.http.orders.batch_cancel(order_ids=['order-id'])                    # cancel
```

`orders.close_position` places a reduce-only market order against an open futures/perpetuals position, sized to close it in full or in part.
