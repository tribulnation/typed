# Listen To Streams

## Market Data

Streams are public — no credentials needed.

```python
from typed_binance import Binance

async with Binance.new(public=True) as client:
  async with client.spot.streams.ticker('BTCUSDT') as stream:
    async for update in stream:
      print(update)
```

`client.spot.streams` also has `kline`, `agg_trade`, `trade`, `partial_depth`, `diff_depth`,
`book_ticker`, `avg_price`, `block_trade`, and `reference_price`, plus `mini_ticker_all` and
`ticker_window_all` for every symbol at once on those two channels. USD-M futures, COIN-M
futures, and options each have their own streams client with the equivalent channels —
`client.usdm_futures.streams`, `client.coinm_futures.streams`, `client.options.streams` —
plus `client.usdm_futures.public_streams` for USD-M's order-book channels specifically
(`book_ticker`, `diff_depth`, `partial_depth`), which live on a second connection there.

### Only The Newest Frame

Every public stream method takes `keep_latest`, off by default. With `keep_latest=True`, a
push arriving before you read the previous one replaces it, and `stream.skipped` counts the
replaced ones; replaced pushes are never parsed or validated.

You decide when that is safe: only when each push is the full state for that subscription,
such as `book_ticker`, `partial_depth` (`depth` on options) or the per-symbol `mark_price`.
It is wrong for `diff_depth`, trades, klines, liquidations, and the all-symbol streams whose
frames carry different symbols: `book_ticker_arr` (`!bookTicker`, one symbol per frame) and
`mark_price_arr` (`!markPrice@arr`, crypto and TradFi symbols in separate frames). Dropping
a frame there loses data.

```python
from typed_binance import Binance

async with Binance.new(public=True) as client:
  streams = client.usdm_futures.public_streams
  async with streams.book_ticker('btcusdt', keep_latest=True) as stream:
    async for ticker in stream:
      print(ticker['b'], ticker['a'], stream.skipped)
```

## Account Events (Spot)

Signed. Subscribing on Spot's WS API connection also pushes this account's order and
balance events on the same connection:

```python
from typed_binance import Binance

async with Binance.new() as client:
  async with client.spot.ws.user_data.events() as events:
    async for event in events:
      print(event)
```

`client.spot.ws` is Spot's WS API — the request/response surface behind
`client.spot.ws.market`, `.trading`, `.account`. `client.spot.ws.user_data` also has
`subscribe_signature()`/`unsubscribe()` (the two RPC calls `events()` drives) and
`session_subscriptions()`/`subscribe_listen_token()`.

USD-M and COIN-M futures have their own WS APIs (`client.usdm_futures.ws`,
`client.coinm_futures.ws`), but they don't mirror this mechanism: their WS API documents a
separate, listenKey-based `userDataStream.start`/`.ping`/`.stop` family instead of Spot's
signed `subscribe`. Use their REST listenKey trio
(`client.usdm_futures.http.account.listen_key_start()`/`client.coinm_futures.http.account.
listen_key_start()`, or the WS API equivalent) plus `client.usdm_futures.private_streams.
user_data(listen_key=...)`/`client.coinm_futures.private_streams.user_data(listen_key=...)`
to receive their account events — see the Private Streams section below.

## Private Streams (USD-M / COIN-M / Options)

Signed, listenKey-based. Mint a listenKey (REST or WS API), then connect a dedicated stream
with it:

```python
from typed_binance import Binance

async with Binance.new() as client:
  listen_key_result = await client.usdm_futures.http.account.listen_key_start()
  listen_key = listen_key_result.get('listenKey')
  assert listen_key is not None
  async with client.usdm_futures.private_streams.user_data(listen_key=listen_key) as events:
    async for event in events:
      print(event)
```

Keep the listenKey alive with a periodic `client.usdm_futures.http.account.
listen_key_keepalive()` call (Binance closes it after 60 minutes of inactivity).
`client.options` mirrors this shape exactly.

COIN-M futures follows the same pattern, with its own real event set (COIN-M settles PnL
per margin asset rather than one shared USDT ledger, so its account/order/margin-call
events carry an extra `i` account-alias field USD-M's equivalents don't have — see
`client.coinm_futures.private_streams.user_data`'s own docstring for the full event
catalog):

```python
from typed_binance import Binance

async with Binance.new() as client:
  listen_key_result = await client.coinm_futures.http.account.listen_key_start()
  listen_key = listen_key_result.get('listenKey')
  assert listen_key is not None
  async with client.coinm_futures.private_streams.user_data(listen_key=listen_key) as events:
    async for event in events:
      print(event)
```

Keep the listenKey alive with a periodic `client.coinm_futures.http.account.
listen_key_keepalive()` call, same as USD-M's.
