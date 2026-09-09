# Listen To Streams

`client.streams` opens its own WebSocket connection for channel subscriptions, separate
from the connection request/reply methods (`market_data`, `trading`, ...) use.

## Public Channel

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  async with client.streams.market_data.ticker('BTC-PERPETUAL', interval='100ms') as stream:
    async for tick in stream:
      print(tick['instrument_name'], tick['last_price'])
```

## Private Channel

Private (`user.*`) channels need credentials — see [API Keys Setup](../api-keys.md):

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  async with client.streams.user.orders_by_instrument(
    'BTC-PERPETUAL', interval='raw'
  ) as stream:
    async for orders in stream:
      for order in orders:
        print(order['order_id'], order['order_state'])
```

## Reaching Any Method Over WebSocket

There's no separate "raw RPC" escape hatch — every request/reply method already takes a
per-call `transport` keyword, so any JSON-RPC method this package exposes as a typed call
is already reachable over WebSocket directly:

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  result = await client.supporting.get_time(transport='ws')
```
