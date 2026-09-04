# Listen To Streams

MEXC exposes separate spot and futures stream surfaces.

Every subscription method returns a `StreamManager` synchronously -- use it as an
async context manager (auto-unsubscribes on exit) or `await` it directly for a
`Stream` you unsubscribe from by hand.

## Listen To Spot Candles

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  async with client.spot.streams.market.candles('BTCUSDT', 'Min1') as stream:
    async for candle in stream:
      print(candle)
```

## Listen To Spot Order Book Updates

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  async with client.spot.streams.market.depth('BTCUSDT', 5) as stream:
    async for book in stream:
      print(book)
```

## Listen To Your Spot Trades

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  async with client.spot.streams.user.trades() as stream:
    async for trade in stream:
      print(trade)
```

## Listen To Futures Tickers

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  async with client.futures.streams.market.all_tickers() as stream:
    async for message in stream:
      print(message['data'][0])
```

## Listen To Your Futures Trades

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  async with client.futures.streams.user.my_trades() as stream:
    async for message in stream:
      print(message['data']['symbol'], message['data']['price'])
```
