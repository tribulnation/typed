# Fetch Market Data

MEXC market data is split between `spot` and `futures`.

For time windows, pass `datetime` objects directly. See [Timestamps](../reference/timestamps.md).

## Fetch Spot Market Data

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  server_time = await client.spot.market.time()
  depth = await client.spot.market.depth(symbol='BTCUSDT', limit=5)
  trades = await client.spot.market.trades(symbol='BTCUSDT', limit=10)
  print(server_time['serverTime'], depth['bids'][0], trades[0]['price'])
```

## Fetch Spot Candles

```python
from datetime import datetime, timedelta
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  end_time = datetime.now()
  start_time = end_time - timedelta(hours=1)
  candles = await client.spot.market.candles(
    symbol='BTCUSDT',
    interval='1m',
    start_time=start_time,
    end_time=end_time,
    limit=60,
  )
  print(candles[-1][4])
```

### Walk A Longer Range

`candles_paged` and `agg_trades_paged` repeat the window you pass until one comes back empty.
Choose a window the endpoint answers in one response — at most `limit` rows — because a wider
one is capped by MEXC and the walk moves on to the next window:

```python
from datetime import datetime, timedelta
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  start_time = datetime.now() - timedelta(hours=6)
  closes = []
  async for page in client.spot.market.candles_paged(
    symbol='BTCUSDT',
    interval='1m',
    start_time=start_time,
    end_time=start_time + timedelta(hours=1),
    limit=1000,
    max_pages=6,
  ):
    closes += [row[4] for row in page]
  print(len(closes))
```

Spot candles walk **forwards** because MEXC returns them oldest first, and aggregate trades walk
**backwards** because it returns those newest first. Both bounds are required: the width you
pass is the step the walk takes.

## Fetch Futures Candles

```python
from datetime import datetime, timedelta
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  end = datetime.now()
  start = end - timedelta(hours=1)
  candles = await client.futures.market.candles(
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
  info = await client.spot.market.exchange_info(symbol='BTCUSDT')
  print(info['symbols'][0]['symbol'])
```

## Fetch Futures Market Data

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  contract = await client.futures.market.contract_info(symbol='BTC_USDT')
  depth = await client.futures.market.depth('BTC_USDT', limit=20)
  rate = await client.futures.market.funding_rate('BTC_USDT')
  if 'data' in contract:
    print(contract['data'])
  if 'data' in depth and 'data' in rate:
    print(depth['data']['bids'][0], rate['data']['fundingRate'])
```

## Fetch Futures Funding History

```python
from typed_mexc import MEXC

async with MEXC.new(public=True) as client:
  history = await client.futures.market.funding_rate_history(
    symbol='BTC_USDT',
    page_num=1,
    page_size=20,
  )
  if 'data' in history:
    print(history['data']['resultList'][0]['fundingRate'])
```
