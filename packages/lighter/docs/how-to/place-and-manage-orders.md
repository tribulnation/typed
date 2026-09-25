# Place & Manage Orders

Orders are signed L2 transactions under `client.tx`. Each call signs locally with your API
key, takes that key's next nonce, and submits. Needs a full client
([Authenticated Setup](../authenticated-setup.md)).

The examples use market `0`, mainnet's ETH perp. Trying them on testnet
(`Lighter.new(network='testnet')`), use `4095`, testnet's ETH perp: market ids differ per
network ([Networks](../authenticated-setup.md#networks)).

## Prices And Sizes Are Scaled Integers

Lighter signs integers, not decimals: a price is scaled by the market's
`supported_price_decimals`, a size by its `supported_size_decimals`. `client.scaler` fetches
both once and converts in both directions:

```python
from decimal import Decimal

from typed_lighter import Lighter

async with Lighter.new() as client:
  eth = await client.scaler(0)
  print(eth.price(Decimal('2650.25')), eth.size(Decimal('0.05')))  # 265025 and 500
  print(eth.price_of(265025))  # Decimal('2650.25')
```

A price or size with more decimals than the market takes raises `BadRequest` rather than
being rounded silently; pass `rounding='floor'`, `'ceiling'` or `'half-even'` to round it.
The market's `min_base_amount` and `min_quote_amount` apply to the unscaled values. See
[Numbers](../reference/numbers.md).

## Place An Order

`create_order` takes one of seven order shapes, told apart by `order_type` (and, for a
limit order, `time_in_force`); each only accepts its own fields (`time_in_force` only on
limit orders, `order_expiry` only on resting ones, `trigger_price` only on stop-loss and
take-profit orders). `client_order_index` is your own id for the order.

```python
from decimal import Decimal

from typed_lighter import Lighter

async with Lighter.new() as client:
  eth = await client.scaler(0)
  await client.tx.create_order({
    'order_type': 'limit',
    'market_index': 0,
    'client_order_index': 1001,
    'base_amount': eth.size(Decimal('0.05')),  # 500
    'is_ask': False,
    'price': eth.price(Decimal('2000')),       # 200000
    'time_in_force': 'post-only',
  })

  await client.tx.create_order({
    'order_type': 'market',
    'market_index': 0,
    'client_order_index': 1002,
    'base_amount': 500,
    'is_ask': True,
    'price': 190_000,          # worst acceptable price
    'reduce_only': True,
  }, transport='ws')

  await client.tx.create_order({
    'order_type': 'stop-loss-limit',
    'market_index': 0,
    'client_order_index': 1003,
    'base_amount': 500,
    'is_ask': True,
    'trigger_price': 180_000,
    'price': 179_000,
    'reduce_only': True,
  })
```

`transport='ws'` sends the transaction over the WebSocket connection the client shares
with its streams; `'http'` (the default) posts it. The other order types are `'take-profit'`,
`'take-profit-limit'` and `'stop-loss'`.

A resting limit order (`LimitOrder`) has a `time_in_force` of `'good-till-time'` or
`'post-only'`, and takes an optional `order_expiry` (5 minutes to 30 days out, 28 days by
default). An immediate-or-cancel limit order (`IocLimitOrder`) fills what it can at the limit
price or better and cancels the rest; it never rests, so it has no `order_expiry` field, and
the type checker rejects one:

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  await client.tx.create_order({
    'order_type': 'limit',
    'market_index': 0,
    'client_order_index': 1004,
    'base_amount': 500,
    'is_ask': False,
    'price': 200_000,
    'time_in_force': 'immediate-or-cancel',
  })
```

An untyped dict that still passes an `order_expiry` with an immediate-or-cancel order is
refused with `BadRequest` before anything is signed.

## Integrator Fees

An integrator (the app or bot operator placing orders for an account) can charge its own
fee on an order, within caps the account first grants it with `client.tx.approve_integrator`.
The `client.tx` order methods take no integrator: sign the order with its `client.signer`
twin, which takes `integrator=` (on `create_order`, `create_grouped_orders` and
`modify_order`), and submit it with `client.tx.send`:

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  async with client.tx.reserve_nonces(1) as reservation:
    signed = client.signer.create_order(
      {
        'order_type': 'limit',
        'market_index': 0,
        'client_order_index': 1005,
        'base_amount': 500,
        'is_ask': False,
        'price': 200_000,
        'time_in_force': 'post-only',
      },
      integrator={'account_index': 12345, 'taker_fee': 500, 'maker_fee': 0},  # 1e-6 units: 0.05%
      nonce=reservation.nonces[0],
      api_key_index=reservation.api_key_index,
    )
    await client.tx.send(signed)
```

Fees are in 1e-6 units and must stay within the approved caps. Signing inside
`reserve_nonces` takes the nonce from the client, as [Batch Transactions](batch-transactions.md)
explains.

## Accepted Is Not Executed

Every transaction returns a `SendTxResponse`. A `200` means Lighter's API server accepted the
signed transaction, not that it executed: the sequencer can still reject it, and a
post-only order can still be cancelled for crossing. The outcome shows up in the account's
orders:

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  receipt = await client.tx.cancel_order(market_index=0, order_index=1001)
  print(receipt['tx_hash'], receipt['predicted_execution_time_ms'])

  active = await client.api.account.orders.active(account_index=client.signer.account_index, market_id=0)
  print([order['status'] for order in active['orders']])
```

For a push view, follow `client.streams.account_all_orders`
([Listen To Streams](listen-to-streams.md)).

## Modify And Cancel

`order_index` accepts either Lighter's `order_index` or your `client_order_index`:

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  await client.tx.modify_order(market_index=0, order_index=1001, base_amount=600, price=199_500)
  await client.tx.cancel_order(market_index=0, order_index=1001, transport='ws')
```

## Cancel All

Three modes, one shape each:

```python
from datetime import datetime, timedelta, timezone

from typed_lighter import Lighter

async with Lighter.new() as client:
  await client.tx.cancel_all_orders({'mode': 'immediate'})                   # every market
  await client.tx.cancel_all_orders({'mode': 'immediate', 'market_index': 0})  # one market

  deadline = datetime.now(timezone.utc) + timedelta(minutes=5)
  await client.tx.cancel_all_orders({'mode': 'scheduled', 'cancel_at': deadline})  # dead man's switch
  await client.tx.cancel_all_orders({'mode': 'abort'})                       # disarm it
```

Signing a new schedule before `cancel_at` pushes the deadline back.

## Grouped Orders

OTO, OCO and OTOCO groups go in one transaction:

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  await client.tx.create_grouped_orders({
    'grouping_type': 'otoco',
    'primary': {
      'order_type': 'limit', 'market_index': 0, 'base_amount': 500, 'is_ask': False,
      'price': 200_000, 'time_in_force': 'post-only',
    },
    'stop_loss': {'order_type': 'stop-loss', 'trigger_price': 190_000, 'price': 185_000},
    'take_profit': {'order_type': 'take-profit-limit', 'trigger_price': 220_000, 'price': 219_000},
  })
```

The stop-loss and take-profit are placed on the opposite side once the primary fills,
sized by the fill, and cancel each other. An `'oto'` group places one `trigger` order the
same way, and an `'oco'` group places a stop-loss and take-profit of one size and side
straight away. Every stop-loss, take-profit and trigger in a group is reduce-only; there
is no `reduce_only` field to set. The group's `order_expiry` applies to those orders and to
a resting limit primary; an immediate-or-cancel primary has none.

## Leverage And Margin

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  await client.tx.update_leverage(market_index=0, initial_margin_fraction=1_000, margin_mode='isolated')  # 10x
  await client.tx.update_margin(market_index=0, usdc_amount=5_000_000, direction='add')  # 5 USDC
```

Upstream reference: [Trading](https://apidocs.lighter.xyz/docs/trading).
