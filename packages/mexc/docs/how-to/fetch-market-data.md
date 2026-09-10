# Fetch Market Data

MEXC market data is split between `spot` and `futures`.

For time windows, pass `datetime` objects directly. See [Timestamps](../reference/timestamps.md).

## Fetch Spot Market Data

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  server_time = await client.spot.http.market.time()
  depth = await client.spot.http.market.depth(symbol='BTCUSDT', limit=5)
  trades = await client.spot.http.market.trades(symbol='BTCUSDT', limit=10)
  print(server_time['serverTime'], depth['bids'][0], trades[0]['price'])
```

## Fetch Spot Candles

```python
from datetime import datetime, timedelta
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  end_time = datetime.now()
  start_time = end_time - timedelta(hours=1)
  candles = await client.spot.http.market.candles(
    symbol='BTCUSDT',
    interval='1m',
    start_time=start_time,
    end_time=end_time,
    limit=60,
  )
  print(candles[-1][4])
```

### Walk A Longer Range

`candles_paged` and `agg_trades_paged` cover the whole range you pass, however many requests
that takes. Each page that comes back full at `limit` moves one bound to the last row seen and
the walk asks again from there; a page shorter than `limit` means the range is exhausted. Iterate
it for one page of rows at a time, or `await` it for every row in one list:

```python
from datetime import datetime, timedelta
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  start_time = datetime.now() - timedelta(hours=6)
  closes = []
  async for rows in client.spot.http.market.candles_paged(
    symbol='BTCUSDT',
    interval='1m',
    start_time=start_time,
    end_time=start_time + timedelta(hours=3),
    limit=500,
  ):
    closes += [row[4] for row in rows]
  print(len(closes))

  trades = await client.spot.http.market.agg_trades_paged(
    symbol='BTCUSDT',
    start_time=start_time,
    end_time=start_time + timedelta(minutes=30),
  )
  print(len(trades))
```

Spot candles walk **forwards**, moving `start_time`, because MEXC keeps the oldest candles when
a range holds more than `limit`; aggregate trades walk **backwards**, moving `end_time`, because
it keeps the newest trades. A row sitting on the moved bound is served twice by MEXC and dropped
once by the walk, so no row is duplicated or skipped. Nothing is ever requested outside the
bounds you pass; leave one out and the walk runs from MEXC's own default for it.

## Fetch Futures Candles

```python
from datetime import datetime, timedelta
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  end = datetime.now()
  start = end - timedelta(hours=1)
  candles = await client.futures.http.market.candles(
    'BTC_USDT',
    interval='Min1',
    start=start,
    end=end,
  )
  if 'data' in candles:
    print(candles['data']['close'][-1])
```

## Fetch Spot Exchange Metadata

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  info = await client.spot.http.market.exchange_info(symbol='BTCUSDT')
  print(info['symbols'][0]['symbol'])
```

## Fetch Futures Market Data

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  contract = await client.futures.http.market.contract_info(symbol='BTC_USDT')
  depth = await client.futures.http.market.depth('BTC_USDT', limit=20)
  rate = await client.futures.http.market.funding_rate('BTC_USDT')
  if 'data' in contract:
    print(contract['data'])
  if 'data' in depth and 'data' in rate:
    print(depth['data']['bids'][0], rate['data']['fundingRate'])
```

## Fetch Futures Funding History

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  history = await client.futures.http.market.funding_rate_history(
    symbol='BTC_USDT',
    page_num=1,
    page_size=20,
  )
  if 'data' in history:
    print(history['data']['resultList'][0]['fundingRate'])
```
