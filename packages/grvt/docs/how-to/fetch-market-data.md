# Fetch Market Data

Everything under `client.market` is public: build the client with `public=True` and no
credentials are needed. Instrument names follow GRVT's readable format, one per kind:

| Kind | Example |
| --- | --- |
| `PERPETUAL` | `BTC_USDT_Perp` |
| `SPOT_SWAP` | `USDC_USDT_SpotSwap` |
| `STABLE_PERP` | `AAPL_USDC_SFP` |
| `FUTURE` | `BTC_USDT_Fut_20Oct23` |
| `CALL`, `PUT` | `ETH_USDT_Call_20Oct23_2800`, `ETH_USDT_Put_20Oct23_2800` |

Which instruments are listed differs per environment; list them (below) for the current
names.

## Instruments And Currencies

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  perps = await client.market.instruments(kind=['PERPETUAL'], is_active=True)
  print(len(perps), perps[0]['instrument'])

  spot = await client.market.all_instruments(kinds=['SPOT_SWAP', 'STABLE_PERP'])
  print([i['instrument'] for i in spot])

  btc = await client.market.instrument('BTC_USDT_Perp')
  print(btc['tick_size'], btc['min_size'], btc['min_notional'])

  currencies = await client.market.currency()
  print([c['symbol'] for c in currencies][:5])

  rules = await client.market.margin_rules('BTC_USDT_Perp')
  print(rules['max_position_size'], rules['risk_brackets'][0]['max_leverage'])
```

The two listings default differently:

1. `instruments()` returns every kind unless you narrow `kind`, and at most `limit` rows
   (500 by default).
2. `all_instruments()` returns only `PERPETUAL` instruments unless you pass `kinds`, as
   above.

Both include delisted instruments (`status` `DELISTED`) unless you pass `is_active=True`.

`margin_rules(instrument)` returns an instrument's maximum position size and risk brackets,
and `supported_assets()` the assets usable in the funding account, in spot trading and as
collateral.

## Tickers

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  ticker = await client.market.ticker('BTC_USDT_Perp')
  print(
    ticker.get('mark_price'), ticker.get('best_bid_price'), ticker.get('best_ask_price')
  )

  mini = await client.market.mini_ticker('BTC_USDT_Perp')
  print(mini.get('last_price'))
```

To follow prices continuously, subscribe to a stream instead of polling (see
[Listen To Live Streams](listen-to-live-streams.md)).

## Order Book

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  book = await client.market.orderbook('BTC_USDT_Perp', depth=10)
  print(book['bids'][0]['price'], book['asks'][0]['price'])
```

`depth` is one of 10, 50, 100 or 500.

## Trades

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  trades = await client.market.trades('BTC_USDT_Perp', limit=100)
  for trade in trades[:3]:
    print(trade['event_time'], trade['price'], trade['size'], trade['is_taker_buyer'])
```

`limit` is required: how many of the most recent trades to return, at most 1000. Older
trades are under `trade_history(instrument=...)`.

## Candles

```python
from datetime import datetime, timedelta, timezone
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  candles = await client.market.candlesticks(
    'BTC_USDT_Perp',
    interval='CI_1_H',
    type='TRADE',
    start_time=datetime.now(timezone.utc) - timedelta(days=1),
  )
  for candle in candles['result'][:3]:
    print(candle['open_time'], candle['open'], candle['close'])
```

Candles come back newest first. `type` is `TRADE`, `MARK`, `INDEX` or `MID`. For a long
range, use `candlesticks_paged` (see [Paginate Through Results](paginate-through-results.md)).

## Funding Rates And Server Time

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  funding = await client.market.funding_rate(instrument='BTC_USDT_Perp', limit=10)
  for row in funding['result']:
    print(row['funding_time'], row['funding_rate'])

  server = await client.market.time()
  print(server['server_time'])
```

## Over WebSocket

Every market data call can also run over GRVT's JSON-RPC WebSocket, with the same arguments
and reply:

```python
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  ticker = await client.market.ticker('BTC_USDT_Perp', transport='ws')
  print(ticker.get('mark_price'))
```

`time()` is HTTP only.
