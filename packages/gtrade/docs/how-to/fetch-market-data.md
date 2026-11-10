# Fetch Market Data

All market data is public: build the client with `public=True`. Trading API prices, sizes
and rates are `Decimal`, timestamps are UTC `datetime`.

Market symbols are `<base>/<quote>` (`BTC/USD`); `BTC-USD` works too.

## Markets

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  markets = await client.trading.markets.list()
  btc = await client.trading.markets.get('BTC/USD')
  print(btc['pairIndex'], btc['maxLeverage'], btc['fees']['openFeeRate'])
  print([c['symbol'] for c in btc['collaterals']])
```

Each market carries what you need before placing an order: leverage bounds, minimum
position size, fees, accepted collaterals and its on-chain `pairIndex`.

## Prices

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  for price in await client.trading.markets.prices():
    print(price['market'], price['mark'], price['index'])
```

`mark` is the execution price; `index` is the oracle price liquidations use.

## Order Book

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  book = await client.trading.markets.book('BTC/USD', levels=10)
  best_bid, best_ask = book['bids'][0], book['asks'][0]
  print(book['markPrice'], best_bid['price'], best_ask['price'], best_ask['cumulativeUsd'])
```

gTrade has no matching engine: the book is virtual, derived from each pair's on-chain
depth bands around the mark price. `levels` ranges from 1 to 30 (default 20).

## Candles

```python
from datetime import datetime, timedelta, timezone
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  now = datetime.now(timezone.utc)
  candles = await client.trading.markets.candles(
    'BTC/USD', interval='1h', from_=now - timedelta(days=1), to=now,
  )
  for candle in candles:
    print(candle['time'], candle['open'], candle['close'])
```

Mark-price OHLC, no volume. Both bounds are required; one request returns the whole window.
Retention depends on the interval (about 14 days of `1m`, 200 days of `1h`, two years of
`1d`); an older window returns an empty list.

## Recent Trades & Funding

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  trades = await client.trading.markets.trades('BTC/USD', limit=50)  # newest first
  funding = await client.trading.markets.funding('BTC/USD')
  print(trades[0]['side'], trades[0]['sizeUsd'], trades[0]['action'])
  print(funding['fundingRateLongHourly'], funding['borrowingRateHourly'], funding['skewUsd'])
```

Funding and borrowing rates are hourly fractions of position size (`0.00001` = 0.001% per hour).

## Price Snapshots

The pricing service returns every pair at once, as arrays indexed by `pairIndex`, with
float prices:

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  btc = await client.trading.markets.get('BTC/USD')
  charts = await client.pricing.snapshots.charts()
  day_ago = await client.pricing.snapshots.prices_24h_ago()
  i = btc['pairIndex']
  print(charts['time'], charts['closes'][i], charts['indexPrices'][i], day_ago['pricesBefore'][i])
```

`charts()` is the current candle of every pair, not candle history; use
`trading.markets.candles` for history.

## Chain & Service Status

```python
from typed_gtrade import GTrade

async with GTrade.new(public=True) as client:
  chain = await client.trading.system.chain()
  health = await client.trading.system.health()
  print(chain['chainId'], chain['diamond'], health['chains'])
```

`chain()` also publishes the EIP-712 signing domain the Trading API verifies.
`system.ready()` answers only when every chain is ready, with each chain's readiness and
order-lifecycle health; otherwise the API answers `503` and it raises `ApiError`.

See the upstream [market data guide](https://docs.gains.trade/developer/trading-api/market-data).
