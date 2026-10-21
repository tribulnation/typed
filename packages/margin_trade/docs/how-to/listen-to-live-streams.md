# Listen To Live Streams

`client.streams` subscribes to Margin Trade's WebSocket channels. Every subscription shares
one connection, opened on the first subscribe. There is no WebSocket login: account
channels take the account address, so a public client can stream any account.

## Order Book

Each `l2_book` push is a full snapshot of the book, not a delta.

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  async with client.streams.l2_book('BTC') as stream:
    async for book in stream:
      bids, asks = book['levels'] or ([], [])  # an empty book answers `levels: []`
      if bids and asks:
        print(book['time'], bids[0]['px'], asks[0]['px'])
```

Leaving the inner `async with` unsubscribes.

## Trades, Prices And Candles

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  async with client.streams.trades('BTC') as stream:
    async for trades in stream:
      for trade in trades:
        print(trade['side'], trade['px'], trade['sz'])
```

The other public channels work the same way:

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  bbo = await client.streams.bbo('BTC')  # best bid and offer
  mids = await client.streams.all_mids()  # every market's mid price
  candles = await client.streams.candle('BTC', interval='1m')  # the open candle as it updates
  async for push in bbo:
    print(push['bbo'][0]['px'], push['bbo'][1]['px'])
    break
  for sub in (bbo, mids, candles):
    await sub.unsubscribe()
```

`await` returns the subscription without a block; call `unsubscribe()` when you are done.

## Your Orders

```python
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  async with client.streams.order_updates(user=address) as stream:
    async for updates in stream:
      for update in updates:
        print(update['order']['oid'], update['order']['coin'], update['status'])
```

One push arrives when an order rests and another when it is canceled or filled.

The client routes `order_updates` pushes by channel alone, not by account: they carry no
account address. Subscribe to `order_updates` for one account per client; for a second
account, open a second `MarginTrade` client. The client routes `active_asset_data` pushes
by account and market (their `user` and `coin`), `user_fills` pushes by account and the
market of their fills, and `web_data3` pushes by the account they name, so several
accounts (and, for `active_asset_data` and `user_fills`, several markets) can share a
connection on those.

## Your Account

```python
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  async with client.streams.active_asset_data(user=address, coin='BTC') as stream:
    async for data in stream:
      print(data['leverage'], data['maxTradeSzs'], data['availableToTrade'])
```

`active_asset_data` and `web_data3` (a full account snapshot) push once on subscribe, then
on every change.

## Your Fills

`user_fills` takes the market as well as the account: the venue pushes fills only to a
subscription that names its `coin`. There is no snapshot on subscribe: each push carries
the new fills as they happen, typically one push per fill. Hold one subscription per
account and market.

```python
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  async with client.streams.user_fills(user=address, coin='BTC') as stream:
    async for push in stream:
      for fill in push['fills']:
        print(fill['time'], fill['side'], fill['px'], fill['sz'], fill['dir'])
```

The server sometimes closes an account-channel connection without warning around a fill.
All of a client's subscriptions share one connection, so this ends every one of them,
public channels included, each with `NetworkError`. To be sure no fill was missed, read
`info.user_fills` after subscribing again.

## Timeouts

Each subscribe and unsubscribe waits for the server's reply up to the client's timeout (10
seconds) and raises `NetworkError` if none arrives. After an unanswered subscribe the client
sends a best-effort unsubscribe for it, so a reply that arrives late does not leave a
subscription streaming on the connection.
