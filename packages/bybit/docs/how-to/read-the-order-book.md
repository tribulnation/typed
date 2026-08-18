# Read The Order Book

Three endpoints return depth, differing in how much of the book they expose and how they treat
retail price improvement (RPI) orders.

| Method | Depth | RPI size |
| --- | --- | --- |
| `market.orderbook` | up to 1000 levels per side (25 for options) | folded into the level |
| `market.full_orderbook` | up to 10000 levels per side | excluded |
| `market.rpi_orderbook` | up to 50 levels per side | reported separately |

## Depth Snapshot

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  book = await client.http.market.orderbook(category='spot', symbol='BTCUSDT', limit=5)
  print(book['s'])
  for price, size in book['b']:
    print('bid', price, size)
  for price, size in book['a']:
    print('ask', price, size)
```

Field names are terse because Bybit's are: `s` is the symbol, `b` the bids, `a` the asks, `ts`
the snapshot time as a millisecond epoch, and `u` the update id that matches the WebSocket
order book stream. Bids are sorted by price descending, asks ascending.

Each level is a `(price, size)` tuple of strings.

## Best Bid And Ask

The top of book is just the first level of each side:

```python
from bybit import Bybit, timestamp

async with Bybit.new(public=True) as client:
  book = await client.http.market.orderbook(category='linear', symbol='BTCUSDT', limit=1)
  (bid, bid_size), (ask, ask_size) = book['b'][0], book['a'][0]
  spread = float(ask) - float(bid)
  print(f'{bid} x {bid_size} | {ask} x {ask_size} | spread {spread:.2f}')
  print(timestamp.parse(book['ts']))
```

`market.tickers` also carries `bid1Price` and `ask1Price` if that is all you need — see
[Read Tickers And Trades](read-tickers.md).

## Full Depth

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  book = await client.http.market.full_orderbook(category='spot', symbol='BTCUSDT')
  print(len(book['b']), len(book['a']))
```

This returns the whole book — expect ten thousand levels per side on a liquid pair, and size the
request budget accordingly. There is no `limit` parameter.

Upstream documents `linear` and `inverse` for this endpoint, but both currently answer with
HTTP 404 and an empty body, which surfaces as a `BadRequest`. In practice only `spot` works.

## RPI Depth

```python
from bybit import Bybit

async with Bybit.new(public=True) as client:
  book = await client.http.market.rpi_orderbook(category='spot', symbol='BTCUSDT', limit=5)
  for price, size, rpi_size in book['b']:
    print('bid', price, size, 'rpi', rpi_size)
```

Levels here are three-column `(price, size, rpi_size)` tuples: the extra column is the size
available only to retail price improvement flow. `limit` is required and ranges from 1 to 50.
