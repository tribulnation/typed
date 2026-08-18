# Timestamps

Coinbase has no single uniform timestamp convention — it follows the specific endpoint,
not the client as a whole.

## Common Patterns

Response timestamp fields come back as `datetime` directly. Coinbase's wire format is
ISO 8601, and pydantic parses it into a `datetime` automatically during response
validation — there's nothing extra to do:

```python
from coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  trades = await client.advanced_trade.products.public.market_trades('BTC-USD', limit=5)
  print(trades['trades'][0]['time'])  # already a datetime
```

Request parameters that take a time are not uniform, though — check the specific
endpoint's signature. Some take a raw UNIX-seconds `int`:

```python
import time
from coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  now = int(time.time())
  candles = await client.advanced_trade.products.public.candles(
    'BTC-USD', start=now - 3600, end=now, granularity='ONE_HOUR',
  )
```

Others take a raw RFC 3339 `str`:

```python
from coinbase import Coinbase

async with Coinbase.new() as client:
  fills = await client.advanced_trade.orders.historical.fills(
    start_sequence_timestamp='2024-01-01T00:00:00Z',
    end_sequence_timestamp='2024-01-02T00:00:00Z',
  )
```

No request parameter accepts a Python `datetime` directly — pass the raw `int` or `str`
value the specific endpoint's signature calls for.
