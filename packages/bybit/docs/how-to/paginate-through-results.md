# Paginate Through Results

Bybit uses exactly two pagination shapes across the public market surface, and **both are done
for you** — each of the five cursor endpoints and each of the six time-window endpoints carries
a `*_paged` async iterator, generated from its spec.

## Cursor Pagination

Five endpoints return an opaque `nextPageCursor`. Pass it back as `cursor` to get the next page;
an **empty string** means there are no further pages.

| Endpoint | Request | Response | Iterator |
| --- | --- | --- | --- |
| `market.instruments` (linear, inverse, option) | `cursor`, `limit` | `nextPageCursor` | `instruments_paged` |
| `market.open_interest` | `cursor`, `limit` | `nextPageCursor` | `open_interest_paged` |
| `market.risk_limit` | `cursor` | `nextPageCursor` | `risk_limit_paged` |
| `market.delivery_price` | `cursor`, `limit` | `nextPageCursor` | `delivery_price_paged` |
| `market.long_short_ratio` | `cursor`, `limit` | `nextPageCursor` | `long_short_ratio_paged` |

`market.instruments` with `category='spot'` is **not** paginated — that variant has no
`nextPageCursor` field at all, and returns every pair in one response.

Each `*_paged` method takes the same arguments as the single-request one minus `cursor`, which
it drives itself, plus an optional `max_pages`. It yields whole pages, so the response type is
unchanged:

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  symbols: list[str] = []
  async for page in client.http.market.instruments_paged(category='linear', limit=200):
    symbols += [i['symbol'] for i in page['list']]
  print(len(symbols))
```

Pass `max_pages` when you only want the first few, which also bounds a walk over a surface that
keeps growing:

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  pages = [
    page
    async for page in client.http.market.open_interest_paged(
      category='linear', symbol='BTCUSDT', interval_time='1h', limit=200, max_pages=3,
    )
  ]
  print(len(pages), sum(len(page['list']) for page in pages))
```

The equivalent hand-written loop, if you want to hold the cursor yourself:

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  symbols: list[str] = []
  cursor = None
  while True:
    page = await client.http.market.instruments(category='linear', limit=200, cursor=cursor)
    assert page['category'] != 'spot'
    symbols += [i['symbol'] for i in page['list']]
    cursor = page['nextPageCursor']
    if not cursor:
      break
  print(len(symbols))
```

Cursor values are URL-encoded key/value pairs such as `first%3D0GUSDT%26last%3D10000SATSUSDT`
or `lastid%3D9826950%26lasttime%3D1785326400`. The format differs per endpoint and is not
stable — **treat cursors as opaque**. Do not parse them, and do not construct one yourself.

## Time-Window Pagination

Six endpoints have no cursor. They take a time window and return the rows inside it, so their
iterators walk by **moving the window you passed**, keeping its width and stepping one
millisecond past the edge just covered.

| Endpoint | Request | Iterator | Note |
| --- | --- | --- | --- |
| `market.kline` | `start`, `end`, `limit` | `kline_paged` | limit 1–1000, default 200 |
| `market.mark_price_kline` | `start`, `end`, `limit` | `mark_price_kline_paged` | limit 1–1000, default 200 |
| `market.index_price_kline` | `start`, `end`, `limit` | `index_price_kline_paged` | limit 1–1000, default 200 |
| `market.premium_index_price_kline` | `start`, `end`, `limit` | `premium_index_price_kline_paged` | limit 1–1000, default 200 |
| `market.funding_history` | `start_time`, `end_time`, `limit` | `funding_history_paged` | limit 1–200, default 200 |
| `market.historical_volatility` | `start_time`, `end_time` | `historical_volatility_paged` | window ≤ 30 days, both or neither |

Pass a first window and the walk repeats it backwards through history until a window comes back
empty. **Both arguments are required here** — the width you choose is the step the walk takes,
so there is no walk without one:

```python
from bybit import Bybit, timestamp

async with Bybit.new(public=True) as client:
  end = timestamp.now()
  rates = []
  async for page in client.http.market.funding_history_paged(
    category='linear', symbol='BTCUSDT',
    start_time=end - 24*60*60*1000, end_time=end, limit=200, max_pages=30,
  ):
    rates += page['list']
  print(len(rates), rates[0]['fundingRateTimestamp'], rates[-1]['fundingRateTimestamp'])
```

Choose a window the endpoint can answer in one response — at most `limit` rows. A wider one is
capped by the venue, and the walk moves on to the next window rather than finishing the one it
truncated. For klines that is `limit` × the interval; the example below walks four minutes of
one-minute candles at a time.

```python
from bybit import Bybit, timestamp

async with Bybit.new(public=True) as client:
  end = timestamp.now()
  async for page in client.http.market.kline_paged(
    category='linear', symbol='BTCUSDT', interval='1',
    start=end - 4*60*1000, end=end, limit=200, max_pages=5,
  ):
    print(len(page['list']), page['list'][0][0], page['list'][-1][0])
```

`market.historical_volatility` walks forwards instead, because it returns its samples oldest
first. It is also stricter — the window must be 30 days or less, and `start_time` and `end_time`
must be supplied together or not at all.

Both bounds of every one of these endpoints are **inclusive**, which is why the iterator steps a
millisecond past each edge. A hand-written loop that reused the previous bound verbatim would
return the boundary row again on every iteration and never finish:

```python
from bybit import Bybit, timestamp

async with Bybit.new(public=True) as client:
  end = timestamp.now()
  start = end - 30*24*60*60*1000
  rates = []
  while True:
    page = await client.http.market.funding_history(
      category='linear', symbol='BTCUSDT',
      start_time=start, end_time=end, limit=200,
    )
    batch = page['list']
    if not batch:
      break
    rates += batch
    end = int(batch[-1]['fundingRateTimestamp']) - 1
    if len(batch) < 200:
      break
  print(len(rates))
```

Write that loop when you want to walk an unbounded stretch of history without choosing a window
width: it moves the bound onto the last row it received, which is a different walk from the
generated one and needs the response to do it.

## Endpoints With No Pagination

`market.tickers`, `market.orderbook`, `market.rpi_orderbook`, `market.full_orderbook`,
`market.recent_trades`, `market.instruments` (spot), `market.insurance`,
`market.new_delivery_price`, `market.index_price_components`, `market.price_limit`,
`market.adl_alert`, `market.fee_group`, and `market.time` return everything in one response.
`limit`, where it exists, truncates rather than pages.
