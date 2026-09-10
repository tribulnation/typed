# Fetch Market Data

Every call below is public: use `Bit2Me.new(public=True)`, no credentials needed.

## Tickers, Order Book, And Recent Trades

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new(public=True) as client:
  tickers = await client.v2.trading.tickers(symbol='BTC/EUR')     # 24h ticker stats
  book = await client.v2.trading.order_book(symbol='BTC/EUR')     # order book
  trades = await client.v1.trading.trades.get_last(symbol='BTC/EUR', limit=5)  # last trades
  print(tickers[0].get('close'), book.get('bids', [])[:1], trades[:1])
```

## Market Config

`v1.trading.markets` returns each market's price/amount precisions and order minimums. Check it before placing an order.

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new(public=True) as client:
  markets = await client.v1.trading.markets(symbol='BTC/EUR')
  print(markets[0].get('tickSize'), markets[0].get('minAmount'))
```

## Candles

```python
from datetime import datetime, timedelta
from typed_bit2me import Bit2Me

end_time = datetime.now()
start_time = end_time - timedelta(hours=1)

async with Bit2Me.new(public=True) as client:
  candles = await client.v1.trading.candles(
    symbol='BTC/EUR',
    interval=1,
    start_time=start_time,
    end_time=end_time,
    limit=60,
  )
  open_time, open_price, high, low, close, volume = candles[-1]
```

Each row is a `(open_time, open, high, low, close, volume)` tuple: `open_time` is a
`datetime`, the rest are the numbers Bit2Me sends. The last row is the current,
still-forming candle. `limit` counts `interval` slots from `start_time`, not rows, so one
call covers at most `limit` candles; `candles_paged()` walks a wider range for you, moving
`start_time` forwards page by page:

```python
from datetime import datetime, timezone
from typed_bit2me import Bit2Me

async with Bit2Me.new(public=True) as client:
  candles = await client.v1.trading.candles_paged(
    symbol='BTC/EUR',
    interval=60,
    start_time=datetime(2026, 6, 1, tzinfo=timezone.utc),
    end_time=datetime(2026, 9, 1, tzinfo=timezone.utc),
    limit=1000,
  )
```

`await` flattens every page into one list; `async for` yields one page's rows at a time.

## Currency Prices, Rates, And Charts

`v1.currency` and `v3.currency` cover cross-currency pricing rather than one market's order book, useful for portfolio valuation or historical charting. Unlike the trading endpoints above, Bit2Me requires credentials for these, so use `Bit2Me.new()`:

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  prices = await client.v1.currency.prices(currency='EUR')          # current + historical prices
  chart = await client.v3.currency.chart(ticker='BTC/EUR', temporality=['one-day'])  # historic price chart
  print(prices, chart[:3])
```
