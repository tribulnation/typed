# Fetch Candles

Bybit exposes four separate kline endpoints. They share the same parameters and the same
positional-row response shape, but each returns a different price series.

| Method | Series | Row |
| --- | --- | --- |
| `market.kline` | traded price | 7 columns |
| `market.mark_price_kline` | mark price | 5 columns |
| `market.index_price_kline` | index price | 5 columns |
| `market.premium_index_price_kline` | premium index | 5 columns |

## Traded Candles

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  candles = await client.http.market.kline(category='spot', symbol='BTCUSDT', interval='60', limit=3)
  for start, open_, high, low, close, volume, turnover in candles['list']:
    print(start, open_, high, low, close, volume, turnover)
```

Rows come back **newest first**. The seven columns are start time, open, high, low, close,
volume, and turnover. Every column is a string, including the start time, which is a
millisecond epoch.

`interval` is a closed set: `'1'`, `'3'`, `'5'`, `'15'`, `'30'`, `'60'`, `'120'`, `'240'`,
`'360'`, `'720'`, `'D'`, `'W'`, `'M'`.

`category` accepts `'spot'`, `'linear'`, and `'inverse'`, and defaults to `'linear'` when
omitted.

## Mark, Index, And Premium Index Candles

These three drop the volume and turnover columns, leaving start time, open, high, low, close:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  mark = await client.http.market.mark_price_kline(category='linear', symbol='BTCUSDT', interval='60', limit=2)
  index = await client.http.market.index_price_kline(category='linear', symbol='BTCUSDT', interval='60', limit=2)
  premium = await client.http.market.premium_index_price_kline(category='linear', symbol='BTCUSDT', interval='60', limit=2)
  print(mark['list'][0])
  print(index['list'][0])
  print(premium['list'][0])
```

`mark_price_kline` also accepts `category='option'`. `index_price_kline` and
`premium_index_price_kline` accept `'linear'` and `'inverse'` only.

## Bounding A Range

`start` and `end` take a real `datetime`, converted to Bybit's millisecond epoch on the wire:

```python
from datetime import datetime, timedelta, timezone
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  end = datetime.now(timezone.utc)
  start = end - timedelta(hours=24)
  candles = await client.http.market.kline(
    category='spot', symbol='BTCUSDT', interval='60',
    start=start, end=end, limit=1000,
  )
  print(len(candles['list']))
```

See [Timestamps](../reference/timestamps.md) for how the row's own leading start-time column
(a plain `str`, unlike the `start`/`end` parameters) converts back into a `datetime`.

`limit` ranges from 1 to 1000 and defaults to 200. A single call can never return more than
`limit` rows, so a long backfill needs a loop — see
[Paginate Through Results](paginate-through-results.md).
