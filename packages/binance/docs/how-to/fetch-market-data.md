# Fetch Market Data

Market data is public — no credentials needed.

```python
from typed_binance import Binance

async with Binance.new(public=True) as client:
  price = await client.spot.market.ticker_price(symbol='BTCUSDT')
  print(price)
```

## Candles

```python
from datetime import datetime, timezone
from typed_binance import Binance

async with Binance.new(public=True) as client:
  candles = await client.spot.market.klines(
    symbol='BTCUSDT',
    interval='1h',
    start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
    end_time=datetime(2026, 1, 2, tzinfo=timezone.utc),
  )
  for candle in candles:
    print(candle)
```

## Order Book & Recent Trades

```python
from typed_binance import Binance

async with Binance.new(public=True) as client:
  book = await client.spot.market.order_book(symbol='BTCUSDT', limit=20)
  trades = await client.spot.market.recent_trades(symbol='BTCUSDT', limit=20)
```

## Tradeable Symbols

```python
from typed_binance import Binance

async with Binance.new(public=True) as client:
  info = await client.spot.market.exchange_info(symbol='BTCUSDT')
  for symbol in info['symbols']:
    print(symbol['symbol'], symbol['status'])
```

`client.spot.market` also exposes `agg_trades`, `ticker_24hr`, `avg_price`, and the rest of
Binance's public spot market data. USD-M futures, COIN-M futures, and options each expose the
equivalent surface under `client.usdm_futures.market`, `client.coinm_futures.market`, and
`client.options.market`.
