# Place & Manage Orders

Placing and cancelling orders needs the signer key (see [Authenticated Setup](../authenticated-setup.md)). The client signs each order's EIP-712 permit and manages nonces; you pass only the order's fields. Orders settle on-chain, so allow a block or two before they show up in `open`.

## Sizes And Prices

Orders are expressed in integer units of the market's increments, not decimals:

- `size_steps` = size / `config['step_size']`
- `price_ticks` = price / `config['step_price']`

On BTC/USDC (`step_size` 0.000001, `step_price` 0.1), 0.0001 BTC at 50,000 USDC is `size_steps=100`, `price_ticks=500000`.

```python
from decimal import Decimal
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  market = (await client.markets.all(market_ids=[1]))['markets'][0]
  size_steps = int(Decimal('0.0001') / market['config']['step_size'])
  price_ticks = int(Decimal('50000') / market['config']['step_price'])
```

`side` is `0` for buy and `1` for sell.

## Place A Limit Order

```python
from typed_risex import RISEx

async with RISEx.new(network='testnet') as client:
  order = await client.orders.place({
    'market_id': 1,
    'order_type': 1,  # limit
    'side': 0,  # buy
    'size_steps': 100,
    'price_ticks': 500000,
    'post_only': True,
  })
  print(order['order_id'], order['tx_hash'])
```

Limit orders default to good-till-cancelled; set `time_in_force` to `1` (GTT, with `ttl_units`), `2` (FOK) or `3` (IOC). `reduce_only`, `stp_mode` (self-trade prevention) and `client_order_id` are optional.

## Place A Market Order

A market order (`order_type: 0`) must be FOK or IOC, and its `price_ticks` is the worst price you accept:

```python
from typed_risex import RISEx

async with RISEx.new(network='testnet') as client:
  order = await client.orders.place({
    'market_id': 1,
    'order_type': 0,  # market
    'time_in_force': 3,  # IOC
    'side': 1,  # sell
    'size_steps': 100,
    'price_ticks': 600000,
    'reduce_only': True,
  })
  print(order['filled_percent'], order['avg_filled_price'])
```

`filled_quantity` and `avg_filled_price` are `int`s scaled by 10^18 (divide by `10**18` for the size and price), and `filled_percent` is a `Decimal`. The venue only reports fills for IOC orders: all three are `''` for any other time in force, and an IOC order that filled nothing has `filled_quantity` `0`.

The two order shapes are separate types, so a market order without `time_in_force`, or one set to rest (`0` GTC), fails type-checking.

## Query Orders

```python
from typed_risex import RISEx

ACCOUNT = '0xYourAccountAddress'
ORDER_ID = '0x...'

async with RISEx.new(network='testnet') as client:
  lookup = await client.orders.get(ORDER_ID)
  print(lookup['order'])
  open_orders = await client.orders.open(account=ACCOUNT, market_id=1)
  for order in open_orders['orders']:
    print(order['order_id'], order['side'], order['size_steps'], order['price_ticks'])
  history = await client.orders.history(account=ACCOUNT, statuses=['ORDER_STATUS_FILLED'], limit=50)
  print(len(history['orders']))
```

## Cancel Orders

```python
from typed_risex import RISEx

ORDER_ID = '0x...'

async with RISEx.new(network='testnet') as client:
  await client.orders.cancel(1, order_id=ORDER_ID)  # one order
  await client.orders.cancel_all(1)  # every resting order in market 1
```

## TP/SL Orders

Take-profit and stop-loss orders live under `client.orders.tpsl` (`place`, `query`, `cancel`, `cancel_all`). They execute through RISEx's OperatorHub, so the account must first grant it a budget with `client.auth.approve_single(...)`, which the account key signs. `place`, `cancel` and `cancel_all` are authorized by a JWT the client logs in for; `query` is public.
