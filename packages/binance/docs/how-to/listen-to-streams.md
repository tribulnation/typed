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
