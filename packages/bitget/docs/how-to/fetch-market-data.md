# Fetch Market Data

All of these are public, no credentials needed.

## Tradeable Symbols

```python
from bitget import Bitget

async with Bitget.new(public=True) as client:
  instruments = await client.uta.market.instruments(category='SPOT')
  one = await client.uta.market.instruments(category='SPOT', symbol='BTCUSDT')
```

`category` is one of `SPOT`, `MARGIN`, `USDT-FUTURES`, `COIN-FUTURES`, `USDC-FUTURES`.

## Order Book

```python
from bitget import Bitget

async with Bitget.new(public=True) as client:
  book = await client.uta.market.orderbook(category='SPOT', symbol='BTCUSDT', limit=50)
```

## Candles

```python
from bitget import Bitget

async with Bitget.new(public=True) as client:
  candles = await client.uta.market.candles(
    category='SPOT', symbol='BTCUSDT', interval='1m',
  )
```

Each candle is a 7-tuple: `(timestamp, open, high, low, close, base_volume, quote_volume)`.
`interval` is one of `1m`, `3m`, `5m`, `15m`, `30m`, `1H`, `4H`, `6H`, `12H`, `1D`. Pass
`type='MARK'` or `type='INDEX'` on a futures `category` for mark/index candles instead of last
traded price.

## Tickers

```python
from bitget import Bitget

async with Bitget.new(public=True) as client:
  tickers = await client.uta.market.tickers(category='SPOT')
  one = await client.uta.market.tickers(category='SPOT', symbol='BTCUSDT')
```

## Recent Trades

```python
from bitget import Bitget

async with Bitget.new(public=True) as client:
  trades = await client.uta.market.fills(category='SPOT', symbol='BTCUSDT', limit=100)
```

## Classic v2

The same data is available for Classic-mode accounts under `client.classic`, split by product
domain instead of a `category` parameter, e.g.:

```python
from bitget import Bitget

async with Bitget.new(public=True) as client:
  symbols = await client.classic.spot.symbols(symbol='BTCUSDT')
  book = await client.classic.spot.orderbook(symbol='BTCUSDT')
```
