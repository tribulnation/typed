# Manage Positions & TP/SL

Closing a position and creating or updating a take-profit/stop-loss are signed with the
wallet, so they need the private key (see [Authenticated Setup](../authenticated-setup.md)).

## List Positions

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  positions = await client.exchange.positions.list(with_tp_sl='yes')
  for position in positions['list']:
    print(position['instrument'], position['side'], position['quantity'], position['leverage'])
```

## Set Leverage

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  result = await client.exchange.positions.set_leverage('BTCUSD', leverage=10)
  print(result)
```

## Close a Position

`close` sends a market order for all or part of the position. Pass the position's current
leverage; it is part of the signed payload.

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  positions = await client.exchange.positions.list()
  for position in positions['list']:
    if position['instrument'] == 'BTCUSD' and position['quantity'] > 0:
      order = await client.exchange.positions.close(
        instrument='BTCUSD', quantity=position['quantity'], leverage=position['leverage']
      )
      print(order['id'])
```

## Take-Profit and Stop-Loss

A TP/SL is not an order: when its trigger price is reached EVEDEX places a market order on
your behalf. Attach it to the whole position with `order=None`, or to one order by id.
`side` is the side of that market order, opposite to the position, and a `quantity` of `0`
closes the whole position.

```python
from typed_evedex import Evedex

async with Evedex.new() as client:
  tp = await client.exchange.tpsl.create(
    'BTCUSD', type='take-profit', side='SELL', quantity='0', price='70000', order=None
  )
  await client.exchange.tpsl.update(
    instrument='BTCUSD', id=tp['id'], type='take-profit', side='SELL', quantity='0', price='71000'
  )
  active = await client.exchange.tpsl.list(instrument='BTCUSD', status='active')
  await client.exchange.tpsl.cancel(instrument='BTCUSD', id=tp['id'])
```

TP/SL legs can also be attached when placing an order, with `tpsl=[...]` on
`place_limit`, `place_market` and `place_stop_limit` (see
[Place & Manage Orders](place-and-manage-orders.md)). All TP/SL orders are cancelled on
liquidation.
