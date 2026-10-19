# Listen To Public Data

Use `client.streams` for public subscription-style updates.

## Listen To Order Book Updates

Use `l2_book()` for order book updates.

```python
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new(public=True) as client:
  async with client.streams.l2_book('BTC') as book:
    async for update in book:
      best_bid = update['levels'][0][0]
      best_ask = update['levels'][1][0]
      print(best_bid['px'], best_ask['px'])
```

If you need more compact aggregation, use the optional `n_sig_figs` and `mantissa` arguments.

Every stream method takes `keep_latest`, off by default. With `keep_latest=True`, a push
arriving before you read the previous one replaces it, and `book.skipped` counts the
replaced ones; replaced pushes are never validated. You decide when that is safe: only when
each push is the full state for that subscription, as with `l2_book` and `bbo`. It is wrong
for trades, fills, order updates and other account events, where dropping a push loses
data.

```python
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new(public=True) as client:
  async with client.streams.l2_book('BTC', keep_latest=True) as book:
    async for update in book:
      print(update['levels'][0][0]['px'], book.skipped)
```

## Listen To Candle Updates

```python
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new(public=True) as client:
  async with client.streams.candle('BTC', interval='1m') as candles:
    async for candle in candles:
      print(candle['s'], candle['i'], candle['c'])
```

## Listen To Market-Wide Mid Prices

```python
from typed_hyperliquid import Hyperliquid

async with Hyperliquid.new(public=True) as client:
  async with client.streams.all_mids() as mids:
    async for update in mids:
      print(update['mids']['BTC'])
```

## Other Public Streams

`client.streams` also exposes:

- `l2_book()` for aggregated order book updates
- `candle()` for live candle updates
- `trades()` for public trade prints
- `all_mids()` for market-wide mid prices
- `bbo()` for best-bid/best-offer updates
- `active_asset_ctx()` and `active_asset_data()` for asset-level live state
