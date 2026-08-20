# Read Tickers And Trades

## One Ticker

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  ticker = await client.http.market.tickers(category='spot', symbol='BTCUSDT')
  assert ticker['category'] == 'spot'
  spot = ticker['list'][0]
  print(spot['lastPrice'], spot['price24hPcnt'], spot['volume24h'])
```

## Every Ticker In A Category

Omit `symbol` to get the whole category in one response. There is no pagination here:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  tickers = await client.http.market.tickers(category='linear')
  print(len(tickers['list']))
  top = sorted(tickers['list'], key=lambda t: float(t['turnover24h']), reverse=True)[:5]
  for t in top:
    print(t['symbol'], t['lastPrice'], t['turnover24h'])
```

## The Response Is Discriminated By Category

Like `market.instruments`, the return type is a union tagged by `category`:

- `SpotTickers` — 24-hour statistics and best quote
- `ContractTickers` — adds open interest, funding rate, next funding time, basis
- `OptionTickers` — adds greeks, implied volatilities, and the underlying price

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  tickers = await client.http.market.tickers(category='linear', symbol='BTCUSDT')
  if tickers['category'] == 'spot':
    print(tickers['list'][0]['lastPrice'])
  elif tickers['category'] == 'option':
    print(tickers['list'][0]['delta'])
  else:
    contract = tickers['list'][0]
    print(contract['fundingRate'], contract['nextFundingTime'], contract['openInterest'])
```

Options are keyed by expiry, so filter them with `base_coin` and optionally `exp_date`:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  tickers = await client.http.market.tickers(category='option', base_coin='BTC')
  print(len(tickers['list']), tickers['list'][0]['symbol'])
```

## The Tape

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  trades = await client.http.market.recent_trades(category='spot', symbol='BTCUSDT', limit=5)
  for trade in trades['list']:
    print(trade['time'], trade['side'], trade['price'], trade['size'])
```

Trades are newest first. `side` is the taker's side, `'Buy'` or `'Sell'`. `limit` is capped at
60 for spot and 1000 elsewhere. Option trades carry the extra `mP`, `iP`, `mIv`, and `iv`
fields and drop `isRPITrade`.

This is a one-shot snapshot of at most a few hundred prints. There is no historical trade
endpoint, and no public trade stream — `client.ws.spot` only streams the order book today, see
[Async Usage](../reference/async-usage.md).

## Price Bands

The band an order must fall inside, for a single symbol:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  band = await client.http.market.price_limit(category='linear', symbol='BTCUSDT')
  print(band['buyLmt'], band['sellLmt'])
```

## Funding And Open Interest

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  funding = await client.http.market.funding_history(category='linear', symbol='BTCUSDT', limit=3)
  for rate in funding['list']:
    print(rate['fundingRateTimestamp'], rate['fundingRate'])

  oi = await client.http.market.open_interest(
    category='linear', symbol='BTCUSDT', interval_time='1h', limit=3,
  )
  for sample in oi['list']:
    print(sample['timestamp'], sample['openInterest'])
```

`interval_time` is one of `'5min'`, `'15min'`, `'30min'`, `'1h'`, `'4h'`, `'1d'`. Both series are
newest first, and both are paginated — funding by time window, open interest by cursor. See
[Paginate Through Results](paginate-through-results.md).
