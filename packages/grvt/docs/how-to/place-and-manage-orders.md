# Place & Manage Orders

Orders need an API key and its signer private key (see [API Keys Setup](../api-keys.md)).
The client signs every order locally (EIP-712) and fills in `sub_account_id` from the
configured trading account when you leave it out.

## Place A Limit Order

```python
import secrets
from decimal import ROUND_UP, Decimal
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  btc = await client.market.instrument('BTC_USDT_Perp')
  price = Decimal('60000')  # a bid far below the market, so it rests on the book
  # the smallest size, in steps of min_size, whose notional reaches min_notional
  steps = (btc['min_notional'] / (price * btc['min_size'])).to_integral_value(ROUND_UP)
  size = btc['min_size'] * max(steps, Decimal(1))

  client_order_id = str(2**63 + secrets.randbelow(2**63))
  ack = await client.trading.create_order(
    {
      'time_in_force': 'GOOD_TILL_TIME',
      'post_only': True,
      'legs': [
        {
          'instrument': 'BTC_USDT_Perp',
          'size': size,
          'limit_price': price,
          'is_buying_asset': True,
        }
      ],
      'metadata': {'client_order_id': client_order_id},
    }
  )
  print(ack.get('state'))
```

Points that differ from most venues:

1. **Track orders by `client_order_id`.** The reply to `create_order` is the order as
   received, `PENDING`, with the placeholder `order_id` `0x00`. Look the order up by your
   `client_order_id` to get its real id and state.
2. **Client order ids should be in `[2**63, 2**64)`.** GRVT reserves the lower half for its
   own UI; the client does not enforce the range. An id that collides with an active order
   is rejected.
3. **Sizes and prices are `Decimal`**, in base-asset units and quote currency respectively,
   sent in plain notation (`Decimal('5E+4')` as `50000`). A `str` is accepted too and sent
   exactly as written, so a signed size or price given as one must be in plain notation
   (`'0.004'`, not `'4E-3'`). Read the instrument's limits first: GRVT refuses a price off its `tick_size` grid, a size
   below `min_size` or too granular, and a notional (size times price) below `min_notional`
   (`2066`), each raised as `BadRequest`. Before sending, the client checks only that the
   price has at most 9 decimals and the size at most the instrument's `base_decimals` (see
   [Error Handling](../reference/error-handling.md#checked-before-sending)).
4. **A `GOOD_TILL_TIME` order expires with its signature**, one day after signing by default.
   Change it client-wide with `Grvt.new(signature_ttl=...)` (at most 30 days), or per order
   by passing `'signature': {'expiration': ...}`.

## Place A Market Order

```python
import secrets
from decimal import Decimal
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  await client.trading.create_order(
    {
      'is_market': True,
      'time_in_force': 'IMMEDIATE_OR_CANCEL',
      'legs': [
        {
          'instrument': 'BTC_USDT_Perp',
          'size': Decimal('0.002'),
          'is_buying_asset': False,
        }
      ],
      'metadata': {'client_order_id': str(2**63 + secrets.randbelow(2**63))},
    }
  )
```

Size a market order above `min_notional` at the current price too. Leave `limit_price` out
of its legs: GRVT refuses a market order with a price, except on `STABLE_PERP` instruments,
where the price is the required slippage bound. A market order is never post-only, and
cannot use `RETAIL_PRICE_IMPROVEMENT`. A limit leg without a price, or a market order breaking
either rule, does not type-check.

## Look Up An Order

```python
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  order = await client.trading.order({'client_order_id': '9300000000000000001'})
  print(order.get('order_id'))
  if state := order.get('state'):
    print(state['status'], state['traded_size'], state['reject_reason'])
```

Pass `{'order_id': ...}` once you know the real id. `status` is `PENDING`, `OPEN`, `FILLED`,
`REJECTED` or `CANCELLED`; `UNSPECIFIED` appears only on the not-yet-processed orders a bulk
create returns (see [Bulk Orders](#bulk-orders)). `reject_reason` is a plain string, since
GRVT keeps adding reasons.

## List Open Orders

```python
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  orders = await client.trading.open_orders(kind=['PERPETUAL'], base=['BTC'])
  for order in orders:
    print(order['metadata']['client_order_id'], order['legs'][0].get('limit_price'))
```

## Cancel Orders

```python
from typed_grvt import Grvt

async with Grvt.new(env='testnet') as client:
  await client.trading.cancel_order({'client_order_id': '9300000000000000001'})
  await client.trading.cancel_all_orders(base=['BTC'])
```

`cancel_order` takes `client_order_id`, `order_id` or both. Its optional `time_to_live_ms`
applies only to a cancel by `client_order_id` (see [Bulk Orders](#bulk-orders)); GRVT
ignores it on a cancel by `order_id`. `cancel_all_orders` cancels every open order of the
sub-account, narrowed by `kind`, `base` and `quote`; orders still in
flight may survive it. Both calls only acknowledge the request: confirm the result with
`order(...)` or the `orders` stream.

## Bulk Orders

`bulk_orders(batch)` creates, cancels or cancel-replaces up to 100 orders in one request,
including TP/SL groups; the orders it creates must all be on one instrument. `batch` takes
one of five shapes, importable from
`typed_grvt.trading.bulk_orders`:

| Shape | Does |
| --- | --- |
| `BulkCreate` | create `orders` |
| `BulkCancelByOrderIds`, `BulkCancelByClientOrderIds` | cancel by `order_i_ds` or by `client_order_i_ds` |
| `BulkCancelReplaceByOrderIds`, `BulkCancelReplaceByClientOrderIds` | cancel by either id list, then create `orders` |

`order_i_ds` and `client_order_i_ds` are GRVT's own spelling of these keys. `sub_account_id`
is optional, as on every order.

```python
import secrets
from decimal import Decimal
from typed_grvt import Grvt
from typed_grvt.trading.bulk_orders import BulkCancelByClientOrderIds, BulkCreate

async with Grvt.new(env='testnet') as client:
  ids = [str(2**63 + secrets.randbelow(2**63)) for _ in range(2)]
  create: BulkCreate = {
    'orders': [
      {
        'time_in_force': 'GOOD_TILL_TIME',
        'post_only': True,
        'legs': [
          {
            'instrument': 'BTC_USDT_Perp',
            'size': Decimal('0.002'),
            'limit_price': price,
            'is_buying_asset': True,
          }
        ],
        'metadata': {'client_order_id': client_order_id},
      }
      for client_order_id, price in zip(ids, [Decimal('60000'), Decimal('59000')])
    ]
  }
  await client.trading.bulk_orders(create)

  cancel: BulkCancelByClientOrderIds = {
    'client_order_i_ds': ids,
    'time_to_live_ms': '1000',
  }
  reply = await client.trading.bulk_orders(cancel)
  print(reply['cancel_acks'])
```

Created orders come back unprocessed, with the placeholder `order_id` `0x00` and status
`UNSPECIFIED`: look them up by `client_order_id`. Their `metadata.create_time` and
`state.update_time` are unset, which reads as 1970-01-01 UTC (see
[Timestamps](../reference/timestamps.md#unset-timestamps)). A cancel by client order id may
carry a `time_to_live_ms`, during which an order arriving late with one of those ids is
cancelled too. Like every 64-bit integer GRVT takes, it is a numeral string.

## More Order Tools

1. `cancel_on_disconnect(...)` starts a countdown that cancels every open order unless you
   keep refreshing it, a dead man's switch for market makers.
2. `all_initial_leverage()` reads the leverage set per instrument.
3. `set_derisk_mm_ratio(ratio=...)` sets the sub-account's derisk margin to maintenance
   margin ratio. Like an order, it is signed with the signer key.

Every trading call also accepts `transport='ws'` to go through the authenticated trading
WebSocket instead of HTTP.
