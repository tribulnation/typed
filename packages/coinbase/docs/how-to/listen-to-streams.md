# Listen To Streams

Advanced Trade's WebSocket splits into two connections, both reachable under
`client.app.advanced_trade.streams`: `market_data` for public channels, and `user` for the
calling key's own orders and positions.

## Public Channels

`market_data` needs no credentials, on any client:

```python
from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  async with client.app.advanced_trade.streams.market_data.ticker(['BTC-USD']) as stream:
    async for message in stream:
      print(message)
```

Order book updates work the same way, on `level2`:

```python
from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  async with client.app.advanced_trade.streams.market_data.level2(['BTC-USD']) as stream:
    async for message in stream:
      for event in message['events']:
        print(event['type'], event['product_id'])
```

`market_data` also carries `candles`, `heartbeats`, `status`, `ticker_batch`, and `market_trades` — each subscribed with `product_ids` the same way as `ticker`/`level2`.

## Private Channel

`user` carries the calling key's own open-order and futures/perpetuals position updates, and requires credentials:

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  async with client.app.advanced_trade.streams.user.orders() as stream:
    async for message in stream:
      print(message)
```

`user.futures_balance_summary` is a second authenticated channel, for margin/balance updates on a futures account.

Every subscription is a `StreamManager` — `async with ... as stream:` subscribes and auto-unsubscribes on exit; `async for` yields each notification. A rejected subscription (bad channel name, bad credentials) raises `AuthError` or `BadRequest`; a bad argument on a *valid* channel (e.g. an unknown `product_id`) is acknowledged with an empty subscription instead, since Coinbase itself does not reject it.

This is Advanced Trade's own WebSocket. Coinbase Exchange has a separate, single-connection WebSocket Feed under `client.exchange.streams` — see [Fetch Exchange Market Data](fetch-exchange-market-data.md#public-websocket-channels).
