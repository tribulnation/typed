# Listen To Streams

`client.streams` opens its own WebSocket connection for channel subscriptions, separate
from `client.ws`'s request/reply connection.

## Public Channel

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  async with client.streams.market_data.ticker('BTC-PERPETUAL', '100ms') as stream:
    async for tick in stream:
      print(tick['instrument_name'], tick['last_price'])
```

## Private Channel

Private (`user.*`) channels need credentials — see [API Keys Setup](../api-keys.md):

```python
from typed_deribit import Deribit

async with Deribit.new(testnet=True) as client:
  async with client.streams.user.orders_by_instrument('BTC-PERPETUAL', 'raw') as stream:
    async for orders in stream:
      for order in orders:
        print(order['order_id'], order['order_state'])
```

## Escape Hatch

`client.streams.rpc` reaches any JSON-RPC method over the same open connection, for
whatever this package doesn't expose as a typed method:

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  result = await client.streams.rpc.request('public/get_time')
```
