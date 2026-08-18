# Place & Manage Orders

Trading methods are available both over REST (`spot.trading`) and over the authenticated
WebSocket connection (`streams.trading`). Both need credentials -- see
[API Keys Setup](../api-keys.md).

## Place An Order (REST)

```python
from kraken import Kraken

async with Kraken.new() as client:
  order = await client.spot.trading.add_order(
    pair='XBTUSD',
    type='buy',
    ordertype='limit',
    volume='0.0001',
    price='10000',
    validate=True,
  )
  print(order)
```

`validate=True` checks the order without sending it to the matching engine -- no `txid`
comes back. Drop it to place the order for real.

## Place An Order (WebSocket)

```python
from kraken import Kraken

async with Kraken.new() as client:
  result = await client.streams.trading.add_order(
    symbol='XBT/USD',
    side='buy',
    order_type='limit',
    order_qty=0.0001,
    limit_price=10000.0,
    validate=True,
  )
  print(result)
```

Field names differ from REST (`order_qty` vs `volume`, `limit_price` vs `price`,
`symbol` vs `pair`) -- Spot and the WebSocket API are distinct protocols, not one
surface reachable two ways.

## List & Query Orders

```python
from kraken import Kraken

async with Kraken.new() as client:
  open_orders = await client.spot.account.open_orders()
  closed_orders = await client.spot.account.closed_orders()
  one = await client.spot.account.query_orders(txid='O-ABC12-34567')
```

`open_orders`/`closed_orders` return every matching order; `query_orders` looks up a
specific `txid` (or comma-joined list of up to 50). `closed_orders` returns 50 results
at a time, most recent first -- page further back with its `ofs`/`start`/`end`
parameters.

## Amend, Cancel, Cancel All

```python
from kraken import Kraken

async with Kraken.new() as client:
  await client.spot.trading.amend_order(txid='O-ABC12-34567', order_qty='0.0002')
  await client.spot.trading.cancel_order(txid='O-ABC12-34567')
  await client.spot.trading.cancel_all()
```

`amend_order` edits a live order in place, preserving its `txid` and queue priority
where possible. `edit_order` is the older cancel-replace equivalent (issues a new
`txid`) -- kept for compatibility, `amend_order` is preferred. The WebSocket
equivalents (`streams.trading.amend_order`, `.cancel_order`) take the same
identifiers -- `order_id`/`cl_ord_id`/`order_userref` -- and also accept lists to cancel
several orders in one call.

## Batch Orders

```python
from kraken import Kraken

async with Kraken.new() as client:
  await client.spot.trading.add_order_batch(
    pair='XBTUSD',
    orders=[{'ordertype': 'limit', 'type': 'buy', 'volume': '0.0001', 'price': '10000'}],
    validate=True,
  )
  await client.spot.trading.cancel_order_batch(orders=[{'txid': 'O-ABC12-34567'}])
```

`streams.trading.batch_add`/`.batch_cancel` do the same over WebSocket, up to 15 orders
per batch.

## Dead Man's Switch

```python
from kraken import Kraken

async with Kraken.new() as client:
  await client.spot.trading.cancel_all_orders_after(timeout=60)
```

Starts (or resets) a countdown that cancels every one of your orders if it's not reset
before it expires -- protects resting orders against a client-side network failure.
Call again with `timeout=0` to disable it. `streams.trading.cancel_all_orders_after`
does the same over the WebSocket connection.

## Identifying Orders

Every order accepts either Kraken's own `txid`/`order_id`, or a client-supplied
`cl_ord_id`/`order_userref` set at creation time, for later amend/cancel/query calls.
`userref`/`order_userref` is not required to be unique, so it also works as a group tag --
`cancel_order(txid=<userref>)` cancels every order sharing it.
