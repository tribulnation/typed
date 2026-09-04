# Fetch Exchange Market Data

Coinbase Exchange's public REST surface, under `client.exchange.http`, needs no credentials — safe to call on a plain `Coinbase.new()`, since `exchange_public` already defaults to `True`.

```python
from datetime import datetime, timezone

from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  products = await client.exchange.http.products.list()                       # every trading pair
  product = await client.exchange.http.products.get('BTC-USD')                # one product
  currencies = await client.exchange.http.currencies.list()                   # every known currency

  book = await client.exchange.http.products.book('BTC-USD', level=2)         # order book snapshot
  ticker = await client.exchange.http.products.ticker('BTC-USD')              # last trade, best bid/ask
  trades = await client.exchange.http.products.trades(product_id='BTC-USD', limit=50)    # recent trades

  candles = await client.exchange.http.products.candles(
    'BTC-USD', granularity=3600,
    start=datetime(2024, 1, 1, tzinfo=timezone.utc), end=datetime(2024, 1, 1, 6, tzinfo=timezone.utc),
  )
```

`products.book`'s `level` controls how much detail comes back: `1` (best bid/ask only), `2` (top 50 aggregated levels), or `3` (the full, non-aggregated book). `products.candles`' `granularity` is one of `60`/`300`/`900`/`3600`/`21600`/`86400` seconds, and a single request is rejected past 300 buckets.

`products.trades` also accepts `before`/`after` cursors — the value of the `CB-BEFORE`/`CB-AFTER` response header from a previous call — for walking further back or forward through the trade history by hand.

## Public WebSocket Channels

The Exchange WebSocket Feed serves both public and private channels over one connection, under `client.exchange.streams`. `ticker` and `heartbeat` need no credentials:

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  async with client.exchange.streams.ticker(product_ids=['BTC-USD']) as stream:
    async for message in stream:
      print(message['price'])
```

`auction`, `matches`, `ticker_batch`, and `level2_batch` are the other product-scoped public channels, each subscribed with `product_ids` the same way. `status` takes no arguments at all, and `rfq_matches`' `product_ids` is optional — omit it to receive RFQ matches for every product.
