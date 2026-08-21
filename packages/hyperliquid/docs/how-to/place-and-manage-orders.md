# Place & Manage Orders

Use `client.exchange.http` (or `client.exchange.ws`, the same actions over the shared
WebSocket connection) for signed trading actions, and `client.info` for read-side order
queries.

```bash
export HYPERLIQUID_PRIVATE_KEY="your_private_key"
```

## Resolve The Asset Id

`client.exchange.http.order()` takes one or more order wire objects, and each order uses Hyperliquid asset ids rather than coin symbols. For perps on the default dex, the asset id is the index in `perp_meta()['universe']`.

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
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new() as client:
  meta = await client.info.perp_meta()
  btc_asset = next(
    idx for idx, asset in enumerate(meta['universe']) if asset['name'] == 'BTC'
  )

  result = await client.exchange.http.order(
    orders=[{
      'a': btc_asset,
      'b': True,
      'p': '90000',
      's': '0.001',
      'r': False,
      't': {'limit': {'tif': 'Gtc'}},
    }],
    grouping='na',
  )

  status = result['response']['data']['statuses'][0]
  print(status)
```

Passing more than one entry in `orders` places them as a batch in one call.

`client.exchange.ws` exposes the exact same methods over the shared WebSocket connection --
useful when you're already streaming and want to avoid opening a separate HTTP round trip:

```python
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new() as client:
  meta = await client.info.perp_meta()
  btc_asset = next(
    idx for idx, asset in enumerate(meta['universe']) if asset['name'] == 'BTC'
  )

  result = await client.exchange.ws.order(
    orders=[{
      'a': btc_asset,
      'b': True,
      'p': '90000',
      's': '0.001',
      'r': False,
      't': {'limit': {'tif': 'Gtc'}},
    }],
    grouping='na',
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

  result = await client.exchange.http.cancel(cancels=[{'a': btc_asset, 'o': oid}])
  print(result['response']['data']['statuses'])
```

## Cancel All Open Orders

Hyperliquid exposes cancel-all as `schedule_cancel()`. Pass a UTC timestamp to arm it, or `None` to remove an existing schedule.

```python
from datetime import datetime, timedelta, timezone
from typed_hyperliquid import Hyperliquid

cancel_at = datetime.now(timezone.utc) + timedelta(seconds=30)

async with Hyperliquid.new() as client:
  result = await client.exchange.http.schedule_cancel(time=cancel_at)
  print(result['type'])
```
