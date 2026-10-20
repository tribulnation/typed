# Listen To Live Streams

`client.streams` opens one WebSocket connection per subscription. Every stream message is
validated and carries a per-connection `seq`; a gap in `seq` means messages were lost, so
resubscribe. If the server closes the connection, the stream raises `NetworkError` after the
messages already received; it never reconnects on its own, so resubscribe then too.

## Order Book

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  async with client.streams.orderbooks('BTC-USD') as stream:
    async for message in stream:
      update = message['data']
      print(message['type'], message['seq'], update['b'][:1], update['a'][:1])
```

The full book starts with a `SNAPSHOT`, then sends `DELTA`s every 100 ms and a fresh snapshot
every minute. In a delta, `q` is the change in size and `c` the new absolute size. Pass
`depth='1'` for best bid and ask snapshots only, every 10 ms. Omit the market to stream every
market at once.

## Trades And Prices

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  async with client.streams.trades('BTC-USD') as stream:
    async for message in stream:
      for trade in message['data']:
        print(trade['T'], trade['S'], trade['p'], trade['q'])
```

The same pattern covers `client.streams.mark_prices(...)`, `index_prices(...)`,
`funding(...)` and `candles('BTC-USD', candle_type='trades', interval='PT1M')`.

## Account Updates

The account stream needs an API key. It pushes order, trade, balance and position changes for
the key's sub-account, including the final status of every order you place.

```python
from typed_extended import Extended

async with Extended.new() as client:
  async with client.streams.account() as stream:
    async for message in stream:
      data = message.get('data') or {}
      if message['type'] == 'ORDER':
        for order in data.get('orders', []):
          print(order['id'], order['status'])
      elif message['type'] == 'TRADE':
        print(data.get('trades'))
```

## Unsubscribing By Hand

Awaiting a stream instead of entering it gives you the subscription to close yourself:

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  stream = await client.streams.mark_prices('BTC-USD')
  async for message in stream:
    print(message)
    break
  await stream.unsubscribe()
```
