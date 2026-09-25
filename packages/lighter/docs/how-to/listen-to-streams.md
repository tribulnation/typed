# Listen To Streams

`client.streams` subscribes to Lighter's WebSocket channels. Every subscription shares one
connection, which `client.tx` also uses when you pass `transport='ws'`.

## Public Channels

No credentials needed:

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  async with client.streams.order_book(0) as book:
    async for frame in book:
      state = frame['order_book']
      print(frame['type'], state['nonce'], state['bids'][:1], state['asks'][:1])
```

Other public channels: `ticker`, `trades`, `candles` and `mark_price_candles` (with a
`resolution`), `market_stats` and `spot_market_stats` (one market or `'all'`), `height`, and
the per-account `account_all`, `account_all_positions`, `account_all_trades`, `user_stats`,
`pool_data` and `pool_info`.

## Snapshot, Then Updates

The first frame of every subscription is a snapshot, typed `subscribed/<channel>`; every
later one is `update/<channel>`. For most channels both share one shape. On `order_book`
an update is a delta: a level with size `0` is removed, and each update's `begin_nonce`
equals the previous frame's `nonce` when nothing was missed.

```python
from decimal import Decimal

from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  bids: dict[Decimal, Decimal] = {}
  async with client.streams.order_book(0) as book:
    async for frame in book:
      if frame['type'] == 'subscribed/order_book':
        bids.clear()
      for level in frame['order_book']['bids']:
        if level['size'] == 0:
          bids.pop(level['price'], None)
        else:
          bids[level['price']] = level['size']
```

`account_all` and `account_all_trades` differ: only their snapshot carries the trade counts
and volumes, and the frame type (`AccountAllSnapshot | AccountAllUpdate`) narrows on `type`.

## Private Channels

`account_market`, `account_orders`, `account_all_orders`, `account_all_assets`,
`account_tx`, `account_spot_avg_entry_prices`, `notifications` and `rfq` need an auth
token. The client attaches one to the subscription for you, derived from your API key or
taken from a read-only token:

```python
from typed_lighter import Lighter

async with Lighter.new() as client:
  async with client.streams.account_all_orders(client.signer.account_index) as orders:
    async for frame in orders:
      for market_id, market_orders in frame['orders'].items():
        for order in market_orders:
          print(market_id, order['client_order_index'], order['status'])
```

## Without `async with`

`await` a subscription to keep it open beyond one block, and unsubscribe explicitly:

```python
from typed_lighter import Lighter

async with Lighter.new(public=True) as client:
  ticker = await client.streams.ticker(0)
  async for frame in ticker:
    print(frame['ticker']['b']['price'], frame['ticker']['a']['price'])
    break
  await ticker.unsubscribe()
```

## Dropped Connections

Subscriptions do not survive a dropped connection. When the socket goes away, every open
stream raises `NetworkError` (straight away while you are reading it, otherwise on its next
read), an in-flight WebSocket transaction raises `NetworkError` too, and the next subscribe
or transaction reconnects on its own. Resubscribe to recover, and treat the new snapshot as
a fresh start:

```python
from typed_lighter import Lighter, NetworkError

async with Lighter.new(public=True) as client:
  while True:
    try:
      async with client.streams.trades(0) as trades:
        async for frame in trades:
          for trade in frame['trades']:
            print(trade['price'], trade['size'])
    except NetworkError:
      continue
```

Leaving a dead subscription is silent: nothing is sent and no connection is opened just to
unsubscribe.

Upstream reference: [WebSocket reference](https://apidocs.lighter.xyz/docs/websocket-reference).
