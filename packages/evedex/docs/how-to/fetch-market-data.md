# Fetch Market Data

All market data is public: build the client with `public=True` and no credentials are
read. Instruments are USD-quoted perpetuals named like `BTCUSD` (`BTCUSD:DEMO` on demo).

## Instruments

```python
from typed_evedex import Evedex

async with Evedex.new(public=True) as client:
  instruments = await client.exchange.market.instruments()
  for instrument in instruments:
    print(instrument['name'])

  btc = await client.exchange.market.instrument('BTCUSD')
  print(btc['markPrice'], btc['maxLeverage'], btc['quantityIncrement'], btc['fundingRate'])
```

`instruments(fields='metrics')` adds market metrics such as the funding rate to every
entry; it is a heavier request.

## Order Book

```python
from typed_evedex import Evedex

async with Evedex.new(public=True) as client:
  book = await client.exchange.market.order_book(instrument='BTCUSD', round_price='10')
  best_bid, best_ask = book['bids'][0], book['asks'][0]
  print(book['t'], best_bid['price'], best_ask['price'])
```

`round_price` groups levels by a price step. `market_level='1'` returns only the best bid
and ask.

## Recent Trades

```python
from typed_evedex import Evedex

async with Evedex.new(public=True) as client:
  trades = await client.exchange.market.recent_trades('BTCUSD')
  for trade in trades[:5]:
    print(trade['createdAt'], trade['side'], trade['fillQuantity'], trade['fillPrice'])
```

## Candles

Candles come from the market-data service. Each row is a tuple
`(open_time, open, close, high, low, volume_usd, volume)`; note that close comes before high.

```python
from datetime import datetime, timedelta, timezone
from typed_evedex import Evedex

now = datetime.now(timezone.utc)
async with Evedex.new(public=True) as client:
  candles = await client.market_data.candles(
    instrument='BTCUSD', group='1h', after=now - timedelta(days=1), before=now
  )
  for open_time, open_, close, high, low, volume_usd, volume in candles:
    print(open_time, open_, high, low, close)
```

Both bounds are inclusive. When the range holds more than `limit` candles, the newest ones
are returned; `candles_paged` walks a longer range for you (see
[Paginate Through Results](paginate-through-results.md)). On the demo environment candle
history needs credentials.

## Exchange State, Coins and Server Time

```python
from typed_evedex import Evedex

async with Evedex.new(public=True) as client:
  info = await client.exchange.market.info()
  print(info['state'], info['fees'])  # any state other than 'active' halts trading

  coins = await client.exchange.market.coins()
  for coin in coins['list']:
    print(coin)

  ping = await client.exchange.ping()
  print(ping['time'])
```
