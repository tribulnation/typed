# Fetch Market Data

Use `client.info` for request-response market data reads.

## Fetch Depth

Use `dex=...` when you want mids or books from a non-default perp dex.

```python
from hyperliquid import Hyperliquid

async with Hyperliquid.http(public=True) as client:
  book = await client.info.l2_book(coin='BTC')
  best_bid = book['levels'][0][0]
  best_ask = book['levels'][1][0]
  print(best_bid['px'], best_ask['px'])
```

## Fetch Candles

```python
from datetime import datetime, timedelta
from hyperliquid import Hyperliquid
from hyperliquid.core import timestamp as ts

end_time = ts.now()
start_time = ts.dump(datetime.now() - timedelta(hours=1))

async with Hyperliquid.http(public=True) as client:
  candles = await client.info.candle_snapshot(
    coin='BTC',
    interval='1m',
    start_time=start_time,
    end_time=end_time,
  )
  print(candles[-1]['c'])
```

## Fetch Current Funding

For the current funding snapshot, `perp_meta_and_asset_ctxs()` returns metadata and live asset contexts together.

```python
from hyperliquid import Hyperliquid

async with Hyperliquid.http(public=True) as client:
  meta, contexts = await client.info.perp_meta_and_asset_ctxs()
  current_funding = {
    asset['name']: ctx['funding']
    for asset, ctx in zip(meta['universe'], contexts)
  }
  print(current_funding['BTC'])
```

If you want the venue-wide next funding snapshot instead, use `predicted_fundings()`.

## Fetch Funding History

```python
from datetime import datetime, timedelta
from hyperliquid import Hyperliquid
from hyperliquid.core import timestamp as ts

end_time = ts.now()
start_time = ts.dump(datetime.now() - timedelta(days=7))

async with Hyperliquid.http(public=True) as client:
  history = await client.info.funding_history(
    coin='BTC',
    start_time=start_time,
    end_time=end_time,
  )
  print(history[-1]['fundingRate'])
```

For longer windows, use `funding_history_paged()`.

```python
from datetime import datetime, timedelta
from hyperliquid import Hyperliquid
from hyperliquid.core import timestamp as ts

end_time = ts.now()
start_time = ts.dump(datetime.now() - timedelta(days=30))

async with Hyperliquid.http(public=True) as client:
  async for chunk in client.info.funding_history_paged(
    coin='BTC',
    start_time=start_time,
    end_time=end_time,
  ):
    print(len(chunk))
```
