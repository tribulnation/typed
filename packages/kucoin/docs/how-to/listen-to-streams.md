# Listen To Streams

`client.streams.spot_margin` carries both public and private Spot/Margin topics over one
connection; `client.streams.futures` carries the Futures connection. Every subscription
returns a `StreamManager` — connect it with `async with` and it unsubscribes
automatically when the block exits.

## Public Topics

No credentials needed:

```python
from kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  async with client.streams.spot_margin.ticker('BTC-USDT') as stream:
    async for update in stream:
      print(update['price'], update['bestBid'], update['bestAsk'])
```

## Private Topics

Private topics need a client built with real credentials — `public=True` raises
`AuthError` before any connection is attempted:

```python
from kucoin import KuCoin

async with KuCoin.new() as client:
  async with client.streams.spot_margin.balance() as stream:
    async for update in stream:
      print(update['currency'], update['available'])
```

One connection serves both public and private topics once it opens with real
credentials — there's no separate "private" socket to reach for.

## Reconnection

A connection KuCoin closes at its 24-hour boundary raises out of the stream like any
other dropped socket; reconnect by opening a new subscription.
