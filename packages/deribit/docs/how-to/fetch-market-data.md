# Fetch Market Data

`market_data` is public — no credentials needed. Every method's response is identical
whether it's sent over HTTP (the default) or WebSocket (`transport='ws'`).

## Instruments

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  instruments = await client.market_data.get_instruments(
    currency='BTC', kind='future'
  )
  for instrument in instruments:
    print(instrument['instrument_name'], instrument['is_active'])
```

## Ticker

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  ticker = await client.market_data.ticker(instrument_name='BTC-PERPETUAL')
  print(ticker['last_price'], ticker['mark_price'])
```

## Order Book

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  book = await client.market_data.get_order_book(
    instrument_name='BTC-PERPETUAL', depth=20,
  )
  print(book['bids'][:5], book['asks'][:5])
```

## Recent Trades

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  trades = await client.market_data.get_last_trades_by_currency(
    currency='BTC', kind='future', count=10,
  )
  print(trades['trades'])
```

## Candles

```python
from datetime import datetime, timezone
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  candles = await client.market_data.get_tradingview_chart_data(
    instrument_name='BTC-PERPETUAL',
    start_timestamp=datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc),
    end_timestamp=datetime(2023, 11, 14, 23, 13, 20, tzinfo=timezone.utc),
    resolution='60',
  )
  print(candles.get('open'), candles.get('close'))
```

`get_instruments` returns `instrument_name`s that other market-data and trading calls take
directly.
