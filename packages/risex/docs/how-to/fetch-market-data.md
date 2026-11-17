# Fetch Market Data

Market data is public: build the client with `public=True` and no keys are read. Markets are addressed by numeric `market_id` (`1` is BTC/USDC).

## Markets

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  result = await client.markets.all()
  for market in result['markets']:
    config = market['config']
    print(market['market_id'], config['name'], market['mark_price'], config['step_size'], config['step_price'])
```

Each market carries its configuration (`step_size`, `step_price`, `min_order_size`, `max_leverage`), 24h statistics, mark and index prices, open interest and the current funding rate. Pass `market_ids=[1, 2]` to fetch only some markets.

## Order Book

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  book = await client.markets.orderbook(market_id=1, limit=10)
  best_bid, best_ask = book['bids'][0], book['asks'][0]
  print(best_bid['price'], best_bid['quantity'], best_ask['price'], best_ask['quantity'])
```

Levels are aggregated by price, with `order_count` per level. `limit` caps the levels per side (up to 250).

## Candles

```python
from datetime import datetime, timedelta, timezone
from typed_risex import RISEx

HOUR = 3_600 * 10**9  # candle duration, in nanoseconds

async with RISEx.new(public=True) as client:
  now = datetime.now(timezone.utc)
  result = await client.markets.candles(market_id=1, interval=HOUR, from_=now - timedelta(days=7), to=now)
  for candle in result['data']:
    print(candle['time'], candle['open'], candle['high'], candle['low'], candle['close'], candle['volume'])
```

`interval` is the candle duration as an integer number of nanoseconds (`60 * 10**9` for 1-minute candles, `86_400 * 10**9` for daily ones). Without it, 1-minute candles are returned; without `from_`/`to`, the last hour.

One request returns the whole range, but RISEx caps the number of candles a range may span: 30 days of 1-minute candles works, while 90 days is rejected with `time range is not valid`. Use a coarser `interval` (hourly candles cover more than a year) or split the range into several requests.

## Recent Trades

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  result = await client.markets.trade_history(market_id=1, limit=20)
  for trade in result['trades']:
    print(trade['time'], trade['maker_side'], trade['price'], trade['size'])
```

## Funding Rate History

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  result = await client.markets.funding_rate_history(market_id=1, limit=24)
  for record in result['records']:
    print(record['start_time'], record['funding_rate'])
```

Both histories paginate; see [Paginate Through Results](paginate-through-results.md).

## Exchange Stats

`client.stats` covers exchange-wide volume and trade counts, wallet counts and leaderboards. `stats.wallet_count()` is the exception to public access: it needs a JWT, so it raises `AuthError` on a `public=True` client (see [Authenticated Setup](../authenticated-setup.md)). `client.system.config()` returns the chain id, contract addresses (including the USDC token) and maintenance status.

```python
from typed_risex import RISEx

async with RISEx.new(public=True) as client:
  config = await client.system.config()
  print(config['chain']['chain_id'], config['addresses']['usdc'], config['maintenance_phase'])
```
