# Place & Manage Orders

Use `client.exchange` for signed trading actions (`transport='ws'` sends the same action
over the shared WebSocket connection instead of HTTP), and `client.info` for read-side order
queries.

```bash
export HYPERLIQUID_PRIVATE_KEY="your_private_key"
```

## Resolve The Asset Id

`client.exchange.order()` takes one or more order wire objects, and each order uses Hyperliquid asset ids rather than coin symbols. For perps on the default dex, the asset id is the index in `perp_meta()['universe']`.

```python
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new(public=True) as client:
  meta = await client.info.perp_meta()
  btc_asset = next(
    idx
    for idx, asset in enumerate(meta['universe'])
    if asset['name'] == 'BTC'
  )
```

## Place An Order

`order()` takes a list of order wire objects plus a required `grouping`: `'na'` for
independent orders, or `'normalTpsl'`/`'positionTpsl'` for a take-profit/stop-loss pair.

```python
from decimal import Decimal

from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new() as client:
  meta = await client.info.perp_meta()
  btc_asset = next(
    idx for idx, asset in enumerate(meta['universe']) if asset['name'] == 'BTC'
  )

  result = await client.exchange.order(
    orders=[{
      'a': btc_asset,
      'b': True,
      'p': Decimal('90000'),
      's': Decimal('0.001'),
      'r': False,
      't': {'limit': {'tif': 'Gtc'}},
    }],
    grouping='na',
  )

  response = result['response']
  if isinstance(response, dict):
    status = response['data']['statuses'][0]
    print(status)
```

Passing more than one entry in `orders` places them as a batch in one call.

`transport='ws'` sends the exact same call over the shared WebSocket connection instead --
useful when you're already streaming and want to avoid opening a separate HTTP round trip:

```python
from decimal import Decimal

from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new() as client:
  meta = await client.info.perp_meta()
  btc_asset = next(
    idx for idx, asset in enumerate(meta['universe']) if asset['name'] == 'BTC'
  )

  result = await client.exchange.order(
    orders=[{
      'a': btc_asset,
      'b': True,
      'p': Decimal('90000'),
      's': Decimal('0.001'),
      'r': False,
      't': {'limit': {'tif': 'Gtc'}},
    }],
    grouping='na',
    transport='ws',
  )
```

## Query A Specific Order

Use the account address plus either an order id or a client order id.

```python
from typed_hyperliquid import Hyperliquid

user = '0xYourAccountAddress'
oid = 123456789

async with Hyperliquid.new(public=True) as client:
  order = await client.info.order_status(user=user, oid=oid)
  print(order)
```

## List Open Orders

`open_orders()` returns the compact wire shape. `frontend_open_orders()` includes extra fields such as trigger metadata. Both accept `dex=...` for non-default perp dexes.

```python
from typed_hyperliquid import Hyperliquid

user = '0xYourAccountAddress'

async with Hyperliquid.new(public=True) as client:
  open_orders = await client.info.open_orders(user=user)
  print(len(open_orders))
```

## Cancel An Order

`cancel()` accepts one or more cancel wire objects with the same asset id plus the Hyperliquid order id.

```python
from typed_hyperliquid import Hyperliquid

oid = 123456789

async with Hyperliquid.new() as client:
  meta = await client.info.perp_meta()
  btc_asset = next(
    idx for idx, asset in enumerate(meta['universe']) if asset['name'] == 'BTC'
  )

  result = await client.exchange.cancel(cancels=[{'a': btc_asset, 'o': oid}])
  response = result['response']
  if isinstance(response, dict):
    print(response['data']['statuses'])
```

## Cancel All Open Orders

Hyperliquid exposes cancel-all as `schedule_cancel()`. Pass a UTC timestamp to arm it, or `None` to remove an existing schedule.

```python
from datetime import datetime, timedelta, timezone
from typed_hyperliquid import Hyperliquid

cancel_at = datetime.now(timezone.utc) + timedelta(seconds=30)

async with Hyperliquid.new() as client:
  result = await client.exchange.schedule_cancel(time=cancel_at)
  print(result['type'])
```
