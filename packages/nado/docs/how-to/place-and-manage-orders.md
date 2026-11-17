# Place & Manage Orders

Every order and cancellation is signed with your wallet key (EIP-712) — see
[Authenticated Setup](../authenticated-setup.md). The client fills in the sender
subaccount, the nonce and the signature; you supply the order itself.

> **Real funds:** `Nado.new()` is mainnet, so every order example on this page signs and
> executes on mainnet with real funds; try `Nado.new(network='testnet')` first.

## The Order Struct

| Field | Meaning |
| --- | --- |
| `priceX18` | Limit price times `10**18` (a multiple of the product's `price_increment_x18`) |
| `amount` | Size times `10**18`: positive buys, negative sells (a multiple of `size_increment`) |
| `expiration` | A `datetime` after which the order is cancelled |
| `appendix` | A bitfield carrying the order type and flags (below) |

Read the price tick, size increment and minimum size from `client.gateway.symbols()`.

## Building The Appendix

`appendix` is a 128-bit integer carrying the order type and flags. Build it with
`order_appendix`:

```python
from typed_nado import order_appendix

order_appendix()  # plain limit order (GTC): 1
order_appendix('post_only')  # 1537
order_appendix('ioc', reduce_only=True)  # reduce-only IOC
order_appendix(isolated_margin='25.5')  # isolated, moving 25.5 USDT0 of margin in on first match
order_appendix('ioc', reduce_only=True, trigger='price')  # reduce-only stop or take-profit
order_appendix(trigger='twap', twap_executions=10, twap_slippage='0.005')  # TWAP (always IOC), 0.5% max slippage
```

The order type is `'default'` (rests on the book), `'ioc'`, `'fok'` or `'post_only'`; a
TWAP is always `'ioc'`, its default. An order is either isolated or a TWAP, never both,
and a TWAP needs both `twap_executions` and `twap_slippage`; the type checker refuses any
of these mistakes, and at runtime an out-of-range field or more than 6 decimals in
`isolated_margin`/`twap_slippage` raises `BadRequest`. `builder_id` and `builder_fee_rate`
(in 0.1 bps of notional) share fees with a registered builder.

The layout, from the least significant bit:

| Bits | Meaning |
| --- | --- |
| 0-7 | version, always `1` |
| 8 | isolated margin |
| 9-10 | order type: `0` default, `1` IOC, `2` FOK, `3` post-only |
| 11 | reduce-only |
| 12-13 | trigger type: `0` none, `1` price, `2` TWAP, `3` TWAP with custom amounts |
| 38-47 | builder fee rate |
| 48-63 | builder id |
| 64-127 | a TWAP's execution count (high 32 bits) and slippage times `10**6` (low 32), or an isolated order's margin times `10**6` |

## Place An Order

> **Real funds:** this signs and executes on mainnet with real funds; try `Nado.new(network='testnet')` first.

```python
from datetime import datetime, timedelta, timezone
from typed_nado import Nado, order_appendix

async with Nado.new() as client:
  placed = await client.gateway.place_order(
    product_id=2,  # BTC-PERP
    order={
      'priceX18': 50_000 * 10**18,
      'amount': 2 * 10**15,  # buy 0.002 BTC
      'expiration': datetime.now(timezone.utc) + timedelta(days=1),
      'appendix': order_appendix('post_only'),
    },
    id=42,  # optional client id, echoed on fill and order_update events
  )
  print(placed['digest'])
```

Orders are identified by their `digest`. Pass `spot_leverage=False` to refuse any borrow,
and `transport='ws'` to send it over the gateway WebSocket instead of HTTP.
`place_orders([...])` submits a batch of the same requests.

## Query, Cancel, Replace

> **Real funds:** this signs and executes on mainnet with real funds; try `Nado.new(network='testnet')` first.

```python
from datetime import datetime, timedelta, timezone
from typed_nado import Nado, order_appendix

async with Nado.new() as client:
  digest = '0x...'  # from place_order
  order = await client.gateway.order(2, digest=digest)
  print(order['order_type'], order['unfilled_amount'] / 10**18)

  open_orders = await client.gateway.subaccount_orders(product_id=2)

  await client.gateway.cancel_orders({'productIds': [2], 'digests': [digest]})
  await client.gateway.cancel_product_orders({'productIds': [2]})  # every order on BTC-PERP

  replaced = await client.gateway.cancel_and_place(
    {'productIds': [2], 'digests': [digest]},
    place_order={
      'product_id': 2,
      'order': {
        'priceX18': 49_000 * 10**18,
        'amount': 2 * 10**15,
        'expiration': datetime.now(timezone.utc) + timedelta(days=1),
        'appendix': order_appendix('post_only'),
      },
    },
  )
```

`cancel_and_place` cancels and places atomically. An empty `productIds` list in
`cancel_product_orders` cancels everything on the subaccount.

## Trigger And TWAP Orders

Stop and take-profit orders live on `client.trigger`. Build the appendix with
`trigger='price'` and give the condition:

> **Real funds:** this signs and executes on mainnet with real funds; try `Nado.new(network='testnet')` first.

```python
from datetime import datetime, timedelta, timezone
from typed_nado import Nado, order_appendix

async with Nado.new() as client:
  stop = await client.trigger.place_order(
    product_id=2,
    order={
      'priceX18': 55_000 * 10**18,
      'amount': -2 * 10**15,  # sell 0.002 BTC
      'expiration': datetime.now(timezone.utc) + timedelta(days=7),
      'appendix': order_appendix(reduce_only=True, trigger='price'),
    },
    trigger={'price_trigger': {'price_requirement': {'last_price_below': 56_000 * 10**18}}},
  )

  waiting = await client.trigger.list_trigger_orders(status_types=['waiting_price'])
  for info in waiting['orders']:
    print(info['order'], info['status'])

  await client.trigger.cancel_orders({'productIds': [2], 'digests': [stop['digest']]})
```

Price conditions are `last_price_above/below`, `oracle_price_above/below` and
`mid_price_above/below`. `list_trigger_orders` is a signed read and needs a key.

A TWAP splits an order into IOC slices, one every `interval` seconds. Its appendix takes
`trigger='twap'` with the slice count and the maximum slippage of each slice against the
oracle price. Nado requires a TWAP to be IOC, so `order_appendix` packs it as `'ioc'` and
accepts no other order type:

> **Real funds:** this signs and executes on mainnet with real funds; try `Nado.new(network='testnet')` first.

```python
from datetime import datetime, timedelta, timezone
from typed_nado import Nado, order_appendix

async with Nado.new() as client:
  twap = await client.trigger.place_order(
    product_id=2,
    order={
      'priceX18': 60_000 * 10**18,
      'amount': 10**16,  # buy 0.01 BTC over 10 slices
      'expiration': datetime.now(timezone.utc) + timedelta(hours=1),
      'appendix': order_appendix(
        trigger='twap', twap_executions=10, twap_slippage='0.005'
      ),
    },
    trigger={'time_trigger': {'interval': 60}},
  )
```

With `trigger='twap_custom_amounts'`, list each slice's amount (times `10**18`) in
`time_trigger`'s `amounts`.
