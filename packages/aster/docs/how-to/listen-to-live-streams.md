# Listen To Live Streams

`futures`, `spot` and `prediction` each have two WebSocket routers: `streams` for public
market data and `user_stream` for your own account events.

## Market Streams

No credentials needed. Symbols are accepted in either case (`btcusdt` or `BTCUSDT`). Aster
acknowledges a subscription to an unknown stream name without error, then never pushes to
it, so check the symbol and channel name if a stream stays silent.

```python
from typed_aster import Aster

async with Aster.new(public=True) as client:
  async with client.futures.streams.book_ticker('btcusdt') as stream:
    async for update in stream:
      print(update['b'], update['a'])  # best bid, best ask
```

Available channels, per surface:

- trades: `agg_trade`, and `trade` on spot and prediction
- order book: `partial_depth(symbol, levels=5|10|20)`, `diff_depth`, and on futures `partial_depth_speed`/`diff_depth_speed`
- candles: `kline(symbol, interval=...)`
- tickers: `ticker`, `mini_ticker`, `book_ticker`, and `all_tickers`, `all_mini_tickers`, `all_book_tickers` for every symbol
- futures only: `mark_price`, `all_mark_price`, `force_order`, `all_force_orders`
- prediction only: `event(event_name)` for one prediction event's updates

All market streams of a surface share one connection.

## Your Account Events

The user stream needs a listenKey from the REST `listen_key` router, which your API wallet
signs. See [Authenticated Setup](../authenticated-setup.md).

```python
from typed_aster import Aster

async with Aster.new() as client:
  key = await client.futures.listen_key.start()
  async with client.futures.user_stream.events(key['listenKey']) as events:
    async for event in events:
      if event['e'] == 'ORDER_TRADE_UPDATE':
        print(event['o'])
      elif event['e'] == 'ACCOUNT_UPDATE':
        print(event['a'])
```

Futures pushes order, account, margin-call, configuration and announcement events. Spot
pushes `executionReport` and `outboundAccountPosition`.

A listenKey lives 60 minutes. Keep it alive every 30 minutes or so:

```python
from typed_aster import Aster

async with Aster.new() as client:
  await client.futures.listen_key.keepalive()

  spot_key = await client.spot.listen_key.start()
  await client.spot.listen_key.keepalive(spot_key['listenKey'])
```

## Without A Context Manager

Await the stream instead, and unsubscribe when done:

```python
from typed_aster import Aster

async with Aster.new(public=True) as client:
  stream = await client.spot.streams.kline('btcusdt', interval='1m')
  async for candle in stream:
    print(candle['k'])
    break
  await stream.unsubscribe()
```

## Connection Notes

Aster closes connections after 24 hours. The client reopens a closed connection on next use,
but does not restore its subscriptions, so subscribe again.
