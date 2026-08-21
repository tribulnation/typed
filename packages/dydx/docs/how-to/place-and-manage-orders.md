# Place & Manage Orders

Use this page for trading or write workflows such as creating orders, replacing orders, cancelling orders, or inspecting open orders.

```python
from decimal import Decimal

from typed_dydx import Dydx

async with Dydx.testnet('your testnet mnemonic') as client:
  market = await client.indexer.data.get_market('ETH-USD')
  placed = await client.node.place_order(
    market,
    order={
      'side': 'BUY',
      'size': Decimal('0.001'),
      'price': Decimal('1'),
      'flags': 'LONG_TERM',
      'time_in_force': 'POST_ONLY',
    },
    simulate=True,
  )
  print(placed.order.order_id)
```

Long-term and conditional orders can be placed together in one transaction:

```python
from typed_dydx import Dydx

async with Dydx.testnet('your testnet mnemonic') as client:
  market = await client.indexer.data.get_market('ETH-USD')
  placed = await client.node.place_orders([
    {
      'market': market,
      'order': {
        'side': 'BUY',
        'size': '0.001',
        'price': '1',
        'flags': 'LONG_TERM',
        'time_in_force': 'POST_ONLY',
      },
    },
    {
      'market': market,
      'order': {
        'side': 'SELL',
        'size': '0.001',
        'price': '100000',
        'flags': 'LONG_TERM',
        'time_in_force': 'POST_ONLY',
      },
    },
  ])
  print([order.order_id for order in placed.orders])
```

Short-term orders cannot be batched this way because dYdX rejects transactions
containing more than one short-term `MsgPlaceOrder`.
