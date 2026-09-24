# Place & Manage Orders

Orders are signed by your API wallet, which needs the matching trading permission. See
[Authenticated Setup](../authenticated-setup.md).

## Place An Order

An order is a typed dict. Its `type` decides which fields are required, so a `LIMIT` order
without a `price` fails type-checking.

```python
from decimal import Decimal

from typed_aster import Aster

async with Aster.new() as client:
  order = await client.futures.trade.place_order(
    {
      'symbol': 'BTCUSDT',
      'side': 'BUY',
      'type': 'LIMIT',
      'timeInForce': 'GTC',
      'quantity': Decimal('0.001'),
      'price': Decimal('50000'),
    }
  )
  print(order['orderId'], order['status'])
```

Spot and prediction orders use the same shape through `client.spot.trade.place_order` and
`client.prediction.trade.place_order`. `place_batch_orders` sends up to 5 orders at once.
`client.futures.trade.test_order` validates an order without placing it.

## Query, Modify And Cancel

On futures, the order is identified by `orderId` or `origClientOrderId`:

```python
from decimal import Decimal

from typed_aster import Aster

async with Aster.new() as client:
  order = await client.futures.trade.order({'symbol': 'BTCUSDT', 'orderId': 123456})
  await client.futures.trade.modify_order(
    {
      'symbol': 'BTCUSDT',
      'orderId': 123456,
      'quantity': Decimal('0.001'),
      'price': Decimal('49000'),
    }
  )
  await client.futures.trade.cancel_order({'symbol': 'BTCUSDT', 'orderId': 123456})
```

Spot and prediction take keyword arguments instead:

```python
from typed_aster import Aster

async with Aster.new() as client:
  order = await client.spot.trade.order(symbol='ASTERUSDT', order_id=123456)
  await client.spot.trade.cancel_order(symbol='ASTERUSDT', order_id=123456)
```

## Open Orders And Cancel All

```python
from typed_aster import Aster

async with Aster.new() as client:
  open_orders = await client.futures.trade.open_orders('BTCUSDT')
  await client.futures.trade.cancel_all_open_orders('BTCUSDT')
  # Dead man's switch: cancel everything unless called again within 60 s
  await client.futures.trade.countdown_cancel_all('BTCUSDT', countdown_time=60_000)
```

## Cancel Before It Settles: Caller Nonces

Aster queues each signed request until it settles on chain. Every request carries a nonce
(epoch microseconds), which the client normally draws for you. Choose it yourself on
placement, and you can act on that order while it is still queued:

- `noop(nonce)` burns the nonce, so the queued request with that nonce is dropped (best effort).
- `guarded_cancel_order` only cancels the order placed with that nonce.

```python
import time
from decimal import Decimal

from typed_aster import Aster

async with Aster.new() as client:
  nonce = time.time_ns() // 1000
  order = await client.futures.trade.place_order(
    {
      'symbol': 'BTCUSDT',
      'side': 'SELL',
      'type': 'LIMIT',
      'timeInForce': 'GTC',
      'quantity': Decimal('0.001'),
      'price': Decimal('150000'),
      'nonce': nonce,
    }
  )
  await client.futures.trade.guarded_cancel_order(
    {'symbol': 'BTCUSDT', 'orderId': order['orderId'], 'nonce': nonce}
  )
  # or, while the placement is still queued:
  await client.futures.trade.noop(nonce)
```

A nonce you choose must be unique for this API wallet and within about 60 seconds of server
time (10 seconds on prediction).

## Strategy Orders

Futures also has `client.futures.trade.chase_order` (a post-only order re-pegged to the best
bid or ask) and `client.futures.strategy` for OTO, OCO and OTOCO orders.
