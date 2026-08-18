# Place & Manage Orders

All order endpoints require credentials, so use `Bit2Me.new()`. Check `v1.trading.markets` (see [Fetch Market Data](fetch-market-data.md)) for a symbol's price/amount precision and minimums before placing an order.

## Place, Inspect, And Cancel

```python
from dotenv import load_dotenv
from bit2me import Bit2Me

load_dotenv()

async with Bit2Me.new() as client:
  order = await client.v1.trading.orders.create({          # place an order
    'side': 'buy',
    'symbol': 'BTC/EUR',
    'price': '50000',
    'amount': '0.001',
    'orderType': 'limit',
    'timeInForce': 'GTC',
  })
  order_id = order.get('id')
  assert order_id is not None
  fetched = await client.v1.trading.orders.get(order_id)   # check its status
  open_orders = await client.v1.trading.orders.list(symbol='BTC/EUR', status='open')  # list open orders
  trades = await client.v1.trading.orders.list_trades(order_id)  # trades that filled it
  canceled = await client.v1.trading.orders.cancel(order_id)     # cancel it
  print(fetched.get('status'), len(open_orders), len(trades), canceled.get('status'))
```

`create` accepts `stopPrice` for `stop-limit` orders, `postOnly`, and `amountInQuote` to size a market order in quote currency instead of base. See the method's docstring for the full set.

## Via WebSocket

`client.trading_ws` also places and cancels orders as one-shot commands over the same connection used for [private streams](listen-to-streams.md), useful when you're already holding that connection open and want to avoid a separate HTTP round trip:

```python
from decimal import Decimal
from dotenv import load_dotenv
from bit2me import Bit2Me

load_dotenv()

async with Bit2Me.new() as client:
  async with client.trading_ws as trading:
    await trading.add_order(                        # place an order
      symbol='BTC/EUR', side='buy', type='limit',
      price=Decimal('50000'), amount=Decimal('0.001'),
    )
    await trading.cancel_order(order_id='your-order-id')   # cancel by id
    await trading.cancel_all_orders(symbol='BTC/EUR')       # cancel everything on a symbol
```

`add_orders`/`cancel_orders` send a batch in one command, and `auto_cancel_orders_on_disconnection` arms a dead-man's switch that cancels your open orders if the connection drops.
