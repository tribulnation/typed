# Listen To Streams

`client.ws` groups every Bybit v5 WebSocket connection: `spot`, `linear`, `inverse`, and
`option` for public market data, `spread` and `rfq` for spread-trading and RFQ products,
`finance` for Advanced Earn offer channels, `private` for your own account, and `trade` for
order entry (not a subscription — see below).

Every subscribe-shaped method returns a `StreamManager`. Use `async with` so the
subscription unsubscribes automatically on exit, or `await` it directly and call
`unsubscribe()` yourself when you're done.

## Public Market Streams

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  async with client.ws.spot.orderbook(50, 'BTCUSDT') as book:
    async for update in book:
      print(update['s'], update['u'])
```

`orderbook(depth, symbol)` takes a depth of `1`, `50`, or `200` price levels and yields a
dict with `b`/`a` (changed bid/ask levels), `u` (an increasing update id), and `seq` (a
cross-symbol sequence id).

`await`ing the manager directly leaves the subscription open until you call
`unsubscribe()`:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  book = await client.ws.spot.orderbook(50, 'BTCUSDT')
  async for update in book:
    print(update['s'], update['u'])
    break
  await book.unsubscribe()
```

`ticker(symbol)` yields one 24-hour rolling snapshot per push — `lastPrice`,
`highPrice24h`, `volume24h`, and the rest, all strings:

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  async with client.ws.spot.ticker('BTCUSDT') as tickers:
    async for snapshot in tickers:
      print(snapshot['lastPrice'])
```

`trade(symbol)` yields a list of fills per push, each with `i` (trade id), `T` (fill time,
already a `datetime`), `p`/`v` (price/volume), and `S` (taker side):

```python
from typed_bybit import Bybit

async with Bybit.new(public=True) as client:
  async with client.ws.spot.trade('BTCUSDT') as trades:
    async for prints in trades:
      for t in prints:
        print(t['p'], t['v'], t['S'])
```

`client.ws.linear`, `client.ws.inverse`, and `client.ws.option` expose the same
`orderbook`/`ticker`/`trade`-shaped channels as `spot`, for their respective categories.
`client.ws.spread` and `client.ws.rfq` cover Bybit's spread-trading and RFQ order book,
ticker, and public trade/quote channels the same way.

## Private Streams

`client.ws.private` needs credentials — build with `Bybit.new()` rather than
`public=True`; see [API Keys Setup](../api-keys.md).

```python
from typed_bybit import Bybit

async with Bybit.new() as client:
  async with client.ws.private.wallet() as updates:
    async for update in updates:
      print(update)
```

`wallet()` yields a list of `WalletUpdate`s — `accountType`, `totalEquity`, and a `coin`
list of per-coin balances — whenever your account's balance or margin changes.

`order()` streams your own order lifecycle: creations, fills, cancellations, and
rejections, one push per state change.

## Order Entry (Not A Stream)

`client.ws.trade` is request/reply order entry over WebSocket, not a subscription — see
[Async Usage](../reference/async-usage.md#the-ws-trade-connection) for the full treatment.
