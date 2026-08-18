# Fetch Market Data

`market_data` is public — no credentials needed. It's identical on `client.http` and
`client.ws`.

## Instruments

```python
from deribit import Deribit

async with Deribit.new(public=True) as client:
  instruments = await client.http.market_data.get_instruments(
    currency='BTC', kind='future'
  )
  for instrument in instruments:
    print(instrument['instrument_name'], instrument['is_active'])
```

## Ticker

```python
from deribit import Deribit

async with Deribit.new(public=True) as client:
  ticker = await client.http.market_data.ticker(instrument_name='BTC-PERPETUAL')
  print(ticker['last_price'], ticker['mark_price'])
```

## Order Book

```python
from deribit import Deribit

async with Deribit.new(public=True) as client:
  book = await client.http.market_data.get_order_book(
    instrument_name='BTC-PERPETUAL', depth=20,
  )
  print(book['bids'][:5], book['asks'][:5])
```

## Recent Trades

```python
from deribit import Deribit

async with Deribit.new(public=True) as client:
  trades = await client.http.market_data.get_last_trades_by_currency(
    currency='BTC', kind='future', count=10,
  )
  print(trades['trades'])
```

## Candles

```python
from deribit import Deribit

async with Deribit.new(public=True) as client:
  candles = await client.http.market_data.get_tradingview_chart_data(
    instrument_name='BTC-PERPETUAL',
    start_timestamp=1700000000000,
    end_timestamp=1700003600000,
    resolution='60',
  )
  print(candles.get('open'), candles.get('close'))
```

`get_instruments` returns `instrument_name`s that other market-data and trading calls take
directly.
