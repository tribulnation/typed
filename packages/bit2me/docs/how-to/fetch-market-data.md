# Fetch Market Data

Bit2Me market-data coverage is split across versions.

For public-only usage, construct `Bit2Me.public()`.

## Fetch Tickers

```python
from bit2me import Bit2Me

async with Bit2Me.public() as client:
  tickers = await client.v2.trading.tickers(symbol='BTC/EUR')
  print(tickers[0]['close'])
```

## Fetch The Order Book

```python
from bit2me import Bit2Me

async with Bit2Me.public() as client:
  book = await client.v2.trading.order_book(symbol='BTC/EUR')
  print(book['bids'][0], book['asks'][0])
```

## Fetch Market Config

`v1` market-data endpoints live on the versioned client too.

```python
from bit2me import Bit2Me

async with Bit2Me.public() as client:
  config = await client.v1.trading.markets(symbol='BTC/EUR')
  print(config[0]['tickSize'])
```

## Fetch Candles

```python
from datetime import datetime, timedelta
from bit2me import Bit2Me

end_time = datetime.now()
start_time = end_time - timedelta(hours=1)

async with Bit2Me.public() as client:
  ohlcv = await client.v1.trading.candles(
    symbol='BTC/EUR',
    interval=1,
    start_time=start_time,
    end_time=end_time,
    limit=60,
  )
  print(ohlcv[-1])
```

## Fetch Last Trades

```python
from bit2me import Bit2Me

async with Bit2Me.public() as client:
  last_trades = await client.v1.trading.trades.get_last(symbol='BTC/EUR', limit=5)
  print(last_trades[0])
```
