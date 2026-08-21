# Fetch Market Data

`spot.market_data` is public -- no credentials needed.

## Ticker

```python
from typed_kraken import Kraken

async with Kraken.new(public=True) as client:
  ticker = await client.spot.market_data.ticker(pair='XBTUSD')
  print(ticker['XXBTZUSD'].get('c'))  # last trade [price, lot volume]
```

Kraken keys the response by its own internal pair name (`XXBTZUSD`, not `XBTUSD`).
Leave `pair` unset to get every tradeable pair.

## Order Book

```python
from typed_kraken import Kraken

async with Kraken.new(public=True) as client:
  book = await client.spot.market_data.depth(pair='XBTUSD', count=10)
```

`asks`/`bids` are `[price, volume, timestamp]` rows, best price first.

## Candles

```python
from typed_kraken import Kraken

async with Kraken.new(public=True) as client:
  candles = await client.spot.market_data.ohlc(pair='XBTUSD', interval=60)
```

`interval` is in minutes (`1`, `5`, `15`, `30`, `60`, `240`, `1440`, `10080`, `21600`).
Kraken returns at most the last 720 candles per call -- there is no deeper backfill.

## Recent Trades

```python
from typed_kraken import Kraken

async with Kraken.new(public=True) as client:
  trades = await client.spot.market_data.trades(pair='XBTUSD', count=100)
```

## Asset Pairs

```python
from typed_kraken import Kraken

async with Kraken.new(public=True) as client:
  pairs = await client.spot.market_data.asset_pairs()
```

Use this to look up a pair's tradable name, price/quantity precision, and order minimums
before placing an order.

## Also Available

`spot.market_data` also has `assets()` (asset metadata), `spread()` (recent bid/ask
spread), `system_status()`, and `time()` (server time) -- each a single unparameterized
or lightly-parameterized call, same shape as the ones above.
