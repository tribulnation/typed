# Fetch Market Data

All of `client.info` is public: build the client with `public=True` and no credentials.
Markets are named `BASE-QUOTE`, e.g. `BTC-USD`.

## Markets

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  markets = await client.info.markets()  # every market
  for market in markets:
    config = market['tradingConfig']
    print(
      market['name'],
      market['type'],
      market['status'],
      config['minOrderSize'],
      config['minPriceChange'],
    )
```

Pass a list to filter: `await client.info.markets(['BTC-USD', 'ETH-USD'])`. Perpetual and
spot markets share one shape; `type` tells them apart.

## Ticker And Statistics

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  stats = await client.info.market_stats('BTC-USD')
  print(stats['bidPrice'], stats['askPrice'], stats['lastPrice'])
  print(
    stats['markPrice'],
    stats['indexPrice'],
    stats['fundingRate'],
    stats['nextFundingRate'],
  )
```

## Order Book

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  book = await client.info.orderbook('BTC-USD')
  best_bid, best_ask = book['bid'][0], book['ask'][0]
  print(best_bid['price'], best_bid['qty'], best_ask['price'], best_ask['qty'])
```

## Recent Trades

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  trades = await client.info.trades('BTC-USD')
  for trade in trades:
    print(trade['T'], trade['S'], trade['p'], trade['q'], trade['tT'])
```

## Candles

```python
from datetime import datetime, timezone
from typed_extended import Extended

async with Extended.new(public=True) as client:
  candles = await client.info.candles(
    'BTC-USD',
    candle_type='trades',
    interval='PT1H',
    limit=24,
    end_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
  )
  for candle in candles:
    print(candle['T'], candle['o'], candle['h'], candle['l'], candle['c'])
```

`candle_type` picks the price: `trades`, `mark-prices` or `index-prices`. Intervals run from
`PT1M` to `P30D`. Candles come newest first, at most 10,000 per call; walk back by passing the
oldest `T` as `end_time`.

## Funding And Open Interest

```python
from datetime import datetime, timedelta, timezone
from typed_extended import Extended

async with Extended.new(public=True) as client:
  end = datetime.now(timezone.utc)
  funding = await client.info.funding_rates(
    'BTC-USD', start_time=end - timedelta(days=1), end_time=end
  )
  interest = await client.info.open_interests(
    'BTC-USD', interval='P1H', start_time=end - timedelta(days=1), end_time=end
  )
  print(funding[0]['f'], interest[0])
```

## Assets And Exchange Status

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  assets = await client.info.assets()  # every asset
  price = await client.info.asset_price('BTC')  # one asset's price
  status = await client.info.status()  # exchange status
  print(len(assets), price, status)
```
