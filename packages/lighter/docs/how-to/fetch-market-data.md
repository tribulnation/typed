# Fetch Market Data

Market data lives under `client.api.markets` and needs no credentials. Markets are
addressed by an integer `market_id`; perps and spot share the id space, so read
`market_type` rather than guessing from the id.

## List Markets

`order_books` returns every market's static metadata: symbol, type, fees, minimum sizes, and
the decimals that prices and sizes are scaled by when you place an order.

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  books = await client.api.markets.order_books()
  for book in books['order_books']:
    print(book['market_id'], book['symbol'], book['market_type'], book['status'])

  perps = await client.api.markets.order_books(filter='perp')
  eth = next(b for b in perps['order_books'] if b['symbol'] == 'ETH')
```

## Market Details And Decimals

`order_book_details` adds live figures (last price, open interest, 24h volume, margin
fractions). Perps and spot come back in separate lists:

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  details = await client.api.markets.order_book_details(0)
  for perp in details['order_book_details']:
    print(perp['symbol'], perp['last_trade_price'], perp['open_interest'])
    print(perp['supported_price_decimals'], perp['supported_size_decimals'])
  for spot in details['spot_order_book_details']:
    print(spot['symbol'], spot['last_trade_price'])
```

`supported_price_decimals` and `supported_size_decimals` are what
[Place & Manage Orders](place-and-manage-orders.md) scales by. The `price_decimals` and
`size_decimals` fields are display precision only.

## Order Book

A snapshot of the resting orders at the top of the book, best price first on each side:

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  book = await client.api.markets.order_book_orders(market_id=0, limit=20)
  best_bid, best_ask = book['bids'][0], book['asks'][0]
  print(best_bid['price'], best_ask['price'])
```

For a live book, subscribe to `client.streams.order_book` instead
([Listen To Streams](listen-to-streams.md)).

## Recent Trades

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  trades = await client.api.markets.recent_trades(market_id=0, limit=50)
  for trade in trades['trades'] or []:  # `null` when the market has no trades
    print(trade['timestamp'], trade['price'], trade['size'], trade['type'])
```

## Candles

Candles take a `[start, end)` range and return at most 500, the newest ones when the range
holds more. `count_back` is a minimum, not a limit: when the range holds fewer candles,
Lighter extends it backwards from `end`, so candles from before `start` come back too.
Times are `datetime`s both ways:

```python
from datetime import datetime, timedelta, timezone

from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  end = datetime.now(timezone.utc)
  candles = await client.api.markets.candles(
    market_id=0,
    resolution='1h',
    start_timestamp=end - timedelta(days=1),
    end_timestamp=end,
    count_back=24,
  )
  for candle in candles['c']:
    print(candle['t'], candle.get('o', 0.0), candle.get('v', 0.0))  # zeros are omitted

  marks = await client.api.markets.mark_price_candles(
    market_id=0, resolution='1h', start_timestamp=end - timedelta(days=1), end_timestamp=end, count_back=24
  )
```

Lighter leaves zero values out of a candle, so every field but `t` is optional: read them
with `.get(..., 0.0)`. Candle prices and volumes are JSON numbers and come back as `float`
([Numbers](../reference/numbers.md)).

For wider ranges use `candles_paged`, which walks past the 500-row cap
([Paginate Through Results](paginate-through-results.md)).

## Funding

```python
from datetime import datetime, timedelta, timezone

from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  rates = await client.api.markets.funding_rates()  # Lighter's and other venues' current rates
  for rate in rates['funding_rates']:
    if rate['exchange'] == 'lighter':
      print(rate['market_id'], rate['symbol'], rate['rate'])

  end = datetime.now(timezone.utc)
  history = await client.api.markets.fundings(
    market_id=0, resolution='1h', start_timestamp=end - timedelta(days=1), end_timestamp=end, count_back=24
  )
```

## Exchange-Wide Stats

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  stats = await client.api.markets.exchange_stats()     # 24h volume and trades per market
  assets = await client.api.markets.asset_details()     # asset ids and decimals
  status = await client.api.system.status()             # venue status
```

Upstream reference: [Lighter API docs](https://apidocs.lighter.xyz/).
