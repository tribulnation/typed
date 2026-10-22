# Place & Manage Orders

Creating an order needs a [signing client](../authenticated-setup.md): the client signs the
order, and each take-profit or stop-loss leg, with your Stark key. Cancels need only the API
key. Prices and sizes are `Decimal`; respect the market's `minOrderSize`, `minOrderSizeChange`
and `minPriceChange` from `client.info.markets(...)`.

## Place A Limit Order With TP/SL

```python
from decimal import Decimal
from typed_extended import Extended
from typed_extended.orders.create import LimitOrderRequest

async with Extended.new() as client:
  order: LimitOrderRequest = {
    'type': 'LIMIT',
    'market': 'BTC-USD',
    'side': 'BUY',
    'qty': Decimal('0.001'),
    'price': Decimal('80000'),
    'timeInForce': 'GTT',
    'selfTradeProtectionLevel': 'ACCOUNT',
    'postOnly': True,
    'tpSlType': 'ORDER',
    'takeProfit': {
      'triggerPrice': Decimal('90000'),
      'triggerPriceType': 'MARK',
      'price': Decimal('90000'),
      'priceType': 'LIMIT',
    },
    'stopLoss': {
      'triggerPrice': Decimal('75000'),
      'triggerPriceType': 'MARK',
      'price': Decimal('74500'),
      'priceType': 'MARKET',
    },
  }
  placed = await client.orders.create(order)
  print(placed['id'], placed['externalId'])
```

The client fills what signing needs when you leave it out: `fee` (your maker rate for
post-only orders, taker rate otherwise), `nonce`, `expiryEpochMillis` (one hour from now) and
`id`, your client order id, returned as `externalId`.

`type` selects the order shape: `LIMIT`, `MARKET` (`timeInForce: 'IOC'`, with `price` as the
worst accepted price), `CONDITIONAL` (with a `trigger`) or `TPSL` (standalone legs on an order
or, with `tpSlType: 'POSITION'`, the whole position). To edit an open order, send a new one
with `cancelId` set to the old order's `externalId`; the old order closes as `CANCELLED`.

## Protect A Whole Position

An entire-position TP/SL order sends `qty` and `price` as `0`, is reduce-only and opposes the
position's side. Extended rejects one carrying the position's size (`BadRequest`, code
`1133`).

```python
from decimal import Decimal
from typed_extended import Extended
from typed_extended.orders.create import TpslOrderRequest

async with Extended.new() as client:
  order: TpslOrderRequest = {
    'type': 'TPSL',
    'market': 'BTC-USD',
    'side': 'SELL',  # closes a long
    'qty': Decimal('0'),
    'price': Decimal('0'),
    'timeInForce': 'GTT',
    'selfTradeProtectionLevel': 'ACCOUNT',
    'tpSlType': 'POSITION',
    'reduceOnly': True,
    'takeProfit': {
      'triggerPrice': Decimal('90000'),
      'triggerPriceType': 'MARK',
      'price': Decimal('89900'),
      'priceType': 'LIMIT',
    },
    'stopLoss': {
      'triggerPrice': Decimal('75000'),
      'triggerPriceType': 'MARK',
      'price': Decimal('74500'),
      'priceType': 'LIMIT',
    },
  }
  await client.orders.create(order)
```

## Check An Order

Acceptance is asynchronous: `create` returns once the order is queued, and a rejection shows
up later as `status: 'REJECTED'` with a `statusReason`. Watch it on the
[account stream](listen-to-live-streams.md#account-updates), or query it:

```python
from typed_extended import Extended

async with Extended.new() as client:
  order = await client.account.order(123456789)  # by Extended id
  if order is not None:  # None for an id the venue does not know
    print(order['status'], order.get('filledQty'), order.get('statusReason'))
  same = await client.account.orders_by_external_id('my-order-1')  # by client id
```

## List Open Orders

```python
from typed_extended import Extended

async with Extended.new() as client:
  orders = await client.account.open_orders(['BTC-USD'], side='BUY')
  for order in orders:
    print(order['id'], order['type'], order.get('price'), order['qty'])
```

## Cancel

```python
from typed_extended import Extended

async with Extended.new() as client:
  await client.orders.cancel(123456789)  # by Extended id
  await client.orders.cancel_by_external_id('my-order-1')  # by client id
  await client.orders.mass_cancel(markets=['BTC-USD'])  # every order on some markets
  await client.orders.mass_cancel(cancel_all=True)  # every open order
```

Cancels are asynchronous too: the call acknowledges the request, and the account stream
reports the `CANCELLED` status.

## Dead Man's Switch

```python
from typed_extended import Extended

async with Extended.new() as client:
  await client.orders.dead_man_switch(
    60
  )  # cancel everything unless re-armed within 60 s
  await client.orders.dead_man_switch(0)  # disarm
```

## Leverage

```python
from decimal import Decimal
from typed_extended import Extended

async with Extended.new() as client:
  current = await client.account.leverage(['BTC-USD'])
  await client.account.update_leverage(market='BTC-USD', leverage=Decimal('5'))
  updated = await client.account.leverage(['BTC-USD'])
```

`update_leverage` answers with an empty acknowledgement; read the new value back with
`leverage`.

## RFQ Markets

RFQ markets (`isRfq: true` in `client.info.markets()`) take orders through
`client.orders.create_rfq(...)` instead, with the same request shapes. A market RFQ order
can add `rfqStartPrice`, the price makers are first asked to quote at; `price` stays the
worst accepted price. If no maker quotes within it, the order is cancelled.

```python
from decimal import Decimal
from typed_extended import Extended

async with Extended.new() as client:
  await client.orders.create_rfq(
    {
      'type': 'MARKET',
      'market': 'LINK-USD',
      'side': 'BUY',
      'qty': Decimal('1'),
      'price': Decimal('12.2'),
      'rfqStartPrice': Decimal('11.7'),
      'timeInForce': 'IOC',
      'selfTradeProtectionLevel': 'ACCOUNT',
    }
  )
```
