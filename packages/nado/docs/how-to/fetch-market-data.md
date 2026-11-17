# Fetch Market Data

Every market-data call is public: build the client with `public=True` and no key is needed.

Nado identifies products by integer `product_id` (`0` is the USDT0 quote asset, `2` is
BTC-PERP). Prices and sizes on the gateway and archive are x18 fixed-point integers:
divide by `10**18` to get a human value. The `gateway_v2`/`archive_v2` APIs return plain
floats and name markets by ticker id (`BTC-PERP_USDT0`) instead.

## Products And Symbols

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  symbols = await client.gateway.symbols(product_type='perp')
  btc = symbols['symbols']['BTC-PERP']
  print(btc['product_id'], btc['price_increment_x18'], btc['size_increment'], btc['min_size'])

  products = await client.gateway.all_products()  # full spot and perp state, risk weights included
  print(len(products['spot_products']), len(products['perp_products']))
```

`symbols` gives the trading rules you need to build a valid order: price tick, size
increment, minimum size and trading status.

## Prices

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  price = await client.gateway.market_price(2)
  print(price['bid_x18'] / 10**18, price['ask_x18'] / 10**18)

  prices = await client.gateway.cached_prices([2, 4])  # edge cache, separate rate-limit bucket
  funding = await client.archive.funding_rate(2)
  print(funding['funding_rate_x18'] / 10**18, funding['update_time'])
```

## Order Book

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  liquidity = await client.gateway.market_liquidity(product_id=2, depth=10)
  for price_x18, size_x18 in liquidity['bids'][:3]:
    print(price_x18 / 10**18, size_x18 / 10**18)

  book = await client.gateway_v2.orderbook('BTC-PERP_USDT0', depth=10)  # floats
  print(book['bids'][0], book['asks'][0], book['timestamp'])
```

## Candles

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  candles = await client.archive.candlesticks(product_id=2, granularity=3600, limit=24)
  for candle in candles['candlesticks']:
    print(candle['timestamp'], candle['close_x18'] / 10**18)
```

`granularity` is the candle width in seconds: 60, 300, 900, 3600, 7200, 14400, 86400,
604800 or 2419200. Candles come newest first; pass `max_time` to look further back, or use
`candlesticks_paged` (see [Paginate Through Results](paginate-through-results.md)).

## Tickers And Trades

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  tickers = await client.archive_v2.tickers('perp')
  btc = tickers['BTC-PERP_USDT0']
  print(btc['last_price'], btc['base_volume'])

  trades = await client.archive_v2.trades('BTC-PERP_USDT0', limit=50)
  for trade in trades:
    print(trade['trade_id'], trade['price'], trade['base_filled'])

  pairs = await client.gateway_v2.pairs('perp')
  assets = await client.gateway_v2.assets()
```
