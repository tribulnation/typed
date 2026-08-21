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
  print(candles[-1])
```

Each row is `[time, open, high, low, close, volume]`; the last row is the current, still-forming candle.

## Currency Prices, Rates, And Charts

`v1.currency` and `v3.currency` cover cross-currency pricing rather than one market's order book, useful for portfolio valuation or historical charting. Unlike the trading endpoints above, Bit2Me requires credentials for these, so use `Bit2Me.new()`:

```python
from typed_bit2me import Bit2Me

async with Bit2Me.new() as client:
  prices = await client.v1.currency.prices(currency='EUR')          # current + historical prices
  chart = await client.v3.currency.chart(ticker='BTC/EUR', temporality=['one-day'])  # historic price chart
  print(prices, chart[:3])
```
