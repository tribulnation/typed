# Fetch Futures Market Data

Public Futures REST and Charts calls use `Kraken.new(public=True)` without API keys.
The Futures namespace provides `instruments`, `tickers`, `ticker`, `orderbook`, and
`historical_funding_rates`. Responses retain Kraken's `result` and `serverTime` fields.

```python
from typed_kraken import Kraken

async with Kraken.new(public=True) as client:
  instruments = await client.futures.instruments()
  ticker = await client.futures.ticker('PF_XBTUSD')
  book = await client.futures.orderbook('PF_XBTUSD')
  funding = await client.futures.historical_funding_rates('PF_XBTUSD')
  print(ticker['serverTime'], ticker['ticker'])
  print(funding['rates'][-1])
```

Futures REST numeric prices and funding rates are native Python numbers. Funding
history includes the venue's `relativeFundingRate` and its period `timestamp`;
`fundingRate` is the separate absolute rate. Order-book levels retain their native
ordering. Sort them explicitly if your application requires a different order.

## Chart candles

Discover valid tick types, symbols, and resolutions through `tick_types`, `markets`,
and `resolutions`. Symbols belong to the selected chart tick type.

```python
from datetime import datetime, timedelta, timezone
from typed_kraken import Kraken

async with Kraken.new(public=True) as client:
  tick_types = await client.charts.tick_types()
  markets = await client.charts.markets('trade')
  resolutions = await client.charts.resolutions('trade', symbol='PF_XBTUSD')
  end = datetime.now(timezone.utc)
  page = await client.charts.candles(
    'trade', symbol='PF_XBTUSD', resolution='1m',
    from_=end - timedelta(hours=1), to=end, count=60,
  )
  for candle in page['candles']:
    print(candle['time'], candle['close'], candle['volume'])
  print(page['more_candles'])
```

With response validation enabled, chart OHLC values and volume are `Decimal`, and
candle times are timezone-aware `datetime` values. Request bounds are serialized as
Unix seconds; candle timestamps arrive as Unix milliseconds.

Use explicit `from_`, `to`, and `count` parameters for each page. Observed bounds are
inclusive and pages start at the beginning of the requested range, so reusing the last
candle time repeats that candle. Deduplicate boundary rows or advance by the selected
resolution. `more_candles` indicates additional rows in the requested range. There is
currently no automatic chart pager. An omitted count returned 2000 rows in live checks;
the maximum accepted count has not been established.

This surface covers public market data. Futures trading and Futures WebSocket feeds
are outside its current scope.
