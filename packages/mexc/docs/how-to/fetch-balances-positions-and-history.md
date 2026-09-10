# Fetch Balances, Positions & History

Use `MEXC.new()` when you need authenticated spot and futures account data together.

## Fetch Spot Balances

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  account = await client.spot.http.account.info()
  print(account['balances'][0]['asset'], account['balances'][0]['free'])
```

## Fetch Spot Trade History

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  trades = await client.spot.http.account.trades(symbol='BTCUSDT', limit=100)
  print(trades[0]['id'], trades[0]['price'])
```

## Fetch Futures Assets

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  assets = await client.futures.http.account.assets()
  if 'data' in assets:
    print(assets['data'][0]['currency'], assets['data'][0]['availableBalance'])
```

## Fetch Futures Positions

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  positions = await client.futures.http.position.open()
  if 'data' in positions:
    print(positions['data'][0]['symbol'], positions['data'][0]['holdVol'])
```

## Fetch Futures Trades

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  trades = await client.futures.http.trade.order_deals(
    symbol='BTC_USDT',
    page_num=1,
    page_size=100,
  )
  if 'data' in trades:
    print(trades['data'][0]['symbol'], trades['data'][0]['price'])
```

## Fetch Futures Funding History

```python
from typed_mexc import MEXC

async with MEXC.new() as client:
  history = await client.futures.http.account.funding_records(
    symbol='BTC_USDT',
    page_num=1,
    page_size=100,
  )
  if 'data' in history:
    print(history['data']['resultList'][0]['funding'])
```
