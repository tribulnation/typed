# Fetch Market Data

Market data lives on `client.info` (Margin Trade's own API) and `client.coingecko`
(CoinGecko-standard listings). None of it needs a wallet, so a public client is enough.
Prices and sizes come back as `Decimal`, timestamps as `datetime`.

## Markets

`info.meta` lists every perpetual market. Each market's `index` field is its asset index,
which orders and cancels take as `a`. Read the field rather than counting list positions:
`info.meta_and_asset_ctxs` lists the same markets in a different order.

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  meta = await client.info.meta()
  for market in meta['universe']:
    print(market['index'], market['name'], market['maxLeverage'], market['takerFee'])
```

`info.meta_and_asset_ctxs` adds each market's live context (mark price, funding, open
interest), and `info.spot_meta` lists spot tokens and pairs.

## Order Book

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  book = await client.info.l2_book('BTC', n_sig_figs=5)
  bids, asks = book['levels'] or ([], [])  # an empty book answers `levels: []`
  if bids and asks:
    print(book['time'], bids[0]['px'], asks[0]['px'])
```

An empty book answers `levels: []` and a one-sided book has an empty side, so check both
before indexing on a quiet market.

## Prices

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  mids = await client.info.all_mids()
  print(mids['BTC'])
```

## Candles

```python
from datetime import datetime, timedelta, timezone
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  now = datetime.now(timezone.utc)
  candles = await client.info.candle_snapshot({
    'coin': 'BTC',
    'interval': '1h',
    'startTime': now - timedelta(days=1),
  })
  for candle in candles:
    print(candle['t'], candle['o'], candle['h'], candle['l'], candle['c'], candle['v'])
```

## CoinGecko Listings

The `coingecko` surface follows the CoinGecko exchange-integration format: every contract
with its funding rate and open interest, order books by ticker id, and spot trades.

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  contracts = await client.coingecko.derivatives.contracts()
  for contract in contracts:
    print(contract['ticker_id'], contract['funding_rate'], contract['open_interest'])

  book = await client.coingecko.derivatives.orderbook('BTC-USD', depth=10)
  trades = await client.coingecko.spot.historical_trades('PRL_USDC', limit=20)
```

`funding_rate` is a JSON number on the wire and comes back as a `float`.

## Exchange Status

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  version = await client.public.version()
  leaderboard = await client.public.leaderboard()
  deposits = await client.info.perp_dex_status('')  # total net deposits on the exchange
```
