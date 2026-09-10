# Listen To Streams

`client.streams.spot_margin_public`/`.spot_margin_private` carry Spot/Margin topics, split
by visibility but sharing one physical connection; `client.streams.futures_public`/
`.futures_private` carry the Futures connection the same way. Every subscription returns a
`StreamManager` — connect it with `async with` and it unsubscribes automatically when the
block exits.

## Public Topics

No credentials needed:

```python
from typed_kucoin import KuCoin

async with KuCoin.new(public=True) as client:
  async with client.streams.spot_margin_public.ticker('BTC-USDT') as stream:
    async for update in stream:
      print(update['price'], update['bestBid'], update['bestAsk'])
```

## Private Topics

Private topics need a client built with real credentials — `public=True` raises
`AuthError` before any connection is attempted:

```python
from typed_kucoin import KuCoin

async with KuCoin.new() as client:
  async with client.streams.spot_margin_private.balance() as stream:
    async for update in stream:
      print(update['currency'], update['available'])
```

One physical connection serves both `spot_margin_public` and `spot_margin_private` once it
opens with real credentials — there's no separate socket behind the two attributes.

## Reconnection

A connection KuCoin closes at its 24-hour boundary raises out of the stream like any
other dropped socket; reconnect by opening a new subscription.
