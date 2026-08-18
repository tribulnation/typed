# Listen To Streams

Use `client.indexer.streams` for live indexer WebSocket subscriptions.

```python
from dydx import Dydx

async with Dydx.testnet(public=True) as client:
  stream = await client.indexer.streams.markets()
  print(stream.reply)
  async for item in stream:
    print(item)
```

Available stream helpers include:

- `block_height`
- `markets`
- `trades`
- `candles`
- `orders`
- `subaccounts`
- `parent_subaccounts`

Streams return a typed `Stream` object with the subscription snapshot in
`reply`, an async iterator for updates, and an unsubscribe callback.
