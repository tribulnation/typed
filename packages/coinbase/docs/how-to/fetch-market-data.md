# Fetch Market Data

Advanced Trade's public product catalog, under `app.advanced_trade.http.products.public`, needs no credentials — safe to call from a `public=True` client.

```python
import time

from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  products = await client.app.advanced_trade.http.products.public.list(limit=50)             # tradable products
  product = await client.app.advanced_trade.http.products.public.get('BTC-USD')              # one product
  book = await client.app.advanced_trade.http.products.public.book(product_id='BTC-USD', limit=50)  # order book snapshot
  trades = await client.app.advanced_trade.http.products.public.market_trades('BTC-USD', limit=50)  # recent trades

  now = int(time.time())
  candles = await client.app.advanced_trade.http.products.public.candles(
    'BTC-USD', start=now - 3600, end=now, granularity='ONE_MINUTE',
  )
```

`start`/`end` on `candles` are UNIX timestamps; `granularity` accepts `ONE_MINUTE` through `ONE_DAY`.

## Authenticated Market Data

`app.advanced_trade.http.products` (without `.public`) mirrors the same catalog but requires a CDP API Key. It includes futures and equities the public catalog omits, and adds `best_bid_ask`:

```python
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  products = await client.app.advanced_trade.http.products.list(limit=50)
  quote = await client.app.advanced_trade.http.products.best_bid_ask(product_ids=['BTC-USD'])
```
