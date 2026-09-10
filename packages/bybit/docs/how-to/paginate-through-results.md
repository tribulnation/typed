# Paginate Through Results

Bybit uses exactly two pagination shapes across the public market surface, and **both are done
for you**: each of the five cursor endpoints and each of the five time-range endpoints carries
a `*_paged` method, generated from its spec. Every one returns a `PaginatedResponse`: `async for`
walks it one page of *rows* at a time, and `await` flattens every page into one list. There is no
page cap to pass; `break` out of the loop when you have enough.

## Cursor Pagination

Five endpoints return an opaque `nextPageCursor`. Pass it back as `cursor` to get the next page;
an **empty string** means there are no further pages.

| Endpoint | Request | Response | Method |
| --- | --- | --- | --- |
| `market.instruments` (linear, inverse, option) | `cursor`, `limit` | `nextPageCursor` | `instruments_paged` |
| `market.open_interest` | `cursor`, `limit` | `nextPageCursor` | `open_interest_paged` |
| `market.risk_limit` | `cursor` | `nextPageCursor` | `risk_limit_paged` |
| `market.delivery_price` | `cursor`, `limit` | `nextPageCursor` | `delivery_price_paged` |
| `market.long_short_ratio` | `cursor`, `limit` | `nextPageCursor` | `long_short_ratio_paged` |

`market.instruments` with `category='spot'` is **not** paginated: that variant has no
`nextPageCursor` field at all, and returns every pair in one response. `instruments_paged` still
accepts it, and yields that single response's rows as one page.

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  # Awaited: every row, flattened.
  samples = await client.market.open_interest_paged(
    category='linear', symbol='BTCUSDT', interval_time='1h', limit=200,
  )
  print(len(samples))

  # Iterated: one page of rows at a time.
  async for page in client.market.risk_limit_paged(category='linear'):
    print(len(page), page[0]['id'])

  # Stop early: the walk only fetches what you consume.
  symbols: list[str] = []
  async for page in client.market.instruments_paged(category='linear', limit=200):
    symbols += [i['symbol'] for i in page]
    if len(symbols) >= 1000:
      break
  print(len(symbols))
```

The equivalent hand-written loop, if you want to hold the cursor yourself:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  symbols: list[str] = []
  cursor = None
  while True:
    page = await client.market.instruments(category='linear', limit=200, cursor=cursor)
    assert page['category'] != 'spot'
    symbols += [i['symbol'] for i in page['list']]
    cursor = page['nextPageCursor']
    if not cursor:
      break
  print(len(symbols))
```

Cursor values are URL-encoded key/value pairs such as `first%3D0GUSDT%26last%3D10000SATSUSDT`
or `lastid%3D9826950%26lasttime%3D1785326400`. The format differs per endpoint and is not
stable: **treat cursors as opaque**. Do not parse them, and do not construct one yourself.

## Time-Range Pagination

Five endpoints have no cursor. They take a `start`/`end` range and return the rows inside it,
newest first, and when the range holds more than `limit` rows Bybit keeps the **newest** ones.
Their `_paged` methods walk backwards from `end`: each page that comes back full moves `end` to
that page's earliest timestamp, the request is repeated with your own `start` unchanged, and the
walk stops on the first page shorter than `limit`. The boundary row Bybit re-serves is dropped by
its timestamp, so no row is yielded twice, and nothing is ever requested outside the range you
gave.

| Endpoint | Request | Method | Note |
| --- | --- | --- | --- |
| `market.kline` | `start`, `end`, `limit` | `kline_paged` | limit 1–1000, default 200 |
| `market.mark_price_kline` | `start`, `end`, `limit` | `mark_price_kline_paged` | limit 1–1000, default 200 |
| `market.index_price_kline` | `start`, `end`, `limit` | `index_price_kline_paged` | limit 1–1000, default 200 |
| `market.premium_index_price_kline` | `start`, `end`, `limit` | `premium_index_price_kline_paged` | limit 1–1000, default 200 |
| `market.funding_history` | `start_time`, `end_time`, `limit` | `funding_history_paged` | limit 1–200, default 200 |

Both bounds are optional. Omit `end` and the walk starts from the newest row Bybit has; omit
`start` and it keeps going until Bybit runs out of history. Pages arrive newest first, so a
caller who wants the oldest row first reverses the result.

```python
from datetime import datetime, timedelta, timezone
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  end = datetime.now(timezone.utc)
  rates = await client.market.funding_history_paged(
    category='linear', symbol='BTCUSDT',
    start_time=end - timedelta(days=90), end_time=end, limit=200,
  )
  print(len(rates), rates[0]['fundingRateTimestamp'], rates[-1]['fundingRateTimestamp'])
```

A larger `limit` means fewer requests for the same range. The example below walks a day of
one-minute candles in two requests, printing each page's newest and oldest open time:

```python
from datetime import datetime, timedelta, timezone
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  end = datetime.now(timezone.utc)
  async for page in client.market.kline_paged(
    category='linear', symbol='BTCUSDT', interval='1',
    start=end - timedelta(hours=24), end=end, limit=1000,
  ):
    print(len(page), page[0][0], page[-1][0])
```

`market.historical_volatility` also takes `start_time`/`end_time` (supplied together or not at
all, 30 days apart at most) but has no `_paged` method: Bybit publishes no row cap for it, so a
walk could not tell a full page from the end of the series. Call it once per range instead.

## Checkpoint And Resume

Every `_paged` method also exposes the walk's own state. `.pages()` yields each page with the
state it was fetched from and the state the next page needs; hand that state to `.resume()`
later to carry on where you stopped, without refetching what you already have:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  paging = client.market.risk_limit_paged(category='linear')
  checkpoint = None
  async for page in paging.pages():
    print(len(page.rows))
    checkpoint = page.next
    break

  if checkpoint is not None:
    rest = await paging.resume(checkpoint)
    print(len(rest))
```

## Beyond Market Data

The same cursor pattern shows up well past `market.*`: `trade.open_orders_paged` and
`trade.order_history_paged`, `position.list_paged`, `asset.deposit.record_paged` and
`asset.withdraw.record_paged`, and `account.transaction_log_paged` are all the same
`PaginatedResponse` shape as `market.open_interest_paged` above:

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  orders = await client.trade.order_history_paged(category='spot', limit=50)
  print(len(orders))
```

## Endpoints With No Pagination

`market.tickers`, `market.orderbook`, `market.rpi_orderbook`, `market.full_orderbook`,
`market.recent_trades`, `market.instruments` (spot), `market.insurance`,
`market.new_delivery_price`, `market.index_price_components`, `market.price_limit`,
`market.adl_alert`, `market.fee_group`, and `market.time` return everything in one response.
`limit`, where it exists, truncates rather than pages.
