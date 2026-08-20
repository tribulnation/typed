# Listen To Streams

## Market Data

Streams are public — no credentials needed.

```python
from typed_binance import Binance

async with Binance.new(public=True) as client:
  async with client.streams.ticker('BTCUSDT') as stream:
    async for update in stream:
      print(update)
```

`client.streams` also has `kline`, `agg_trade`, `trade`, `partial_depth`, `diff_depth`,
`book_ticker`, `avg_price`, `block_trade`, and `reference_price`, plus `mini_ticker_all` and
`ticker_window_all` for every symbol at once on those two channels. USD-M futures, COIN-M
futures, and options each have their own streams client with the equivalent channels —
`client.usdm_futures_streams`, `client.coinm_futures_streams`, `client.options_streams` —
plus `client.usdm_futures_public_streams` for USD-M's order-book channels specifically
(`book_ticker`, `diff_depth`, `partial_depth`), which live on a second connection there.

## Account Events

Signed. Subscribing on the WS API connection also pushes this account's order and balance
events on the same connection:

```python
from typed_binance import Binance

async with Binance.new() as client:
  async with client.ws_api.subscribe_user_data() as events:
    async for event in events:
      print(event)
```

`client.ws_api` is Spot's WS API — the request/response surface behind `client.ws_api.market`,
`.trading`, `.account`. `client.usdm_futures_ws_api` and `client.coinm_futures_ws_api` mirror
it for USD-M and COIN-M futures.
