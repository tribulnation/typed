# Fetch Market Data

Every market-data endpoint below is public — no credentials needed.

## Ticker

```python
from kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  ticker = await client.spot.ticker(symbol='BTC-USDT')
  print(ticker['price'], ticker['bestBid'], ticker['bestAsk'])
```

## Order Book

`part_orderbook` returns the top `20` or `100` price levels per side, aggregated by
price — cheaper than `full_orderbook`, which is authenticated and returns every level:

```python
from kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  book = await client.spot.part_orderbook('20', symbol='BTC-USDT')
  print(book['bids'][0], book['asks'][0])
```

## Candles

```python
from kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  candles = await client.spot.klines(
    symbol='BTC-USDT', type='1hour', start_at=1_700_000_000, end_at=1_700_010_000,
  )
  for open_time, open_, close, high, low, volume, turnover in candles:
    print(open_time, close)
```

A single response caps at 1500 rows; use `klines_paged` to walk a wider window
automatically — see [Paginate Through Results](paginate-through-results.md).

## Trading Pairs

```python
from kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  symbols = await client.spot.all_symbols()
  print(len(symbols), symbols[0]['symbol'])
```

`client.futures` and `client.margin.market` expose the equivalent ticker, order book,
and candle endpoints for Futures and Margin.
