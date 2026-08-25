# Timestamps

Coinbase has no single uniform timestamp convention — it follows the specific endpoint,
not the client as a whole.

## Common Patterns

Response timestamp fields come back as `datetime` directly. Coinbase's wire format is
ISO 8601, and pydantic parses it into a `datetime` automatically during response
validation — there's nothing extra to do:

```python
from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  trades = await client.app.advanced_trade.http.products.public.market_trades('BTC-USD', limit=5)
  print(trades['trades'][0]['time'])  # already a datetime
```

Request parameters that take a time are not uniform, though — check the specific
endpoint's signature. Some take a raw UNIX-seconds `int`:

```python
import time
from typed_coinbase import Coinbase

async with Coinbase.new(public=True) as client:
  now = int(time.time())
  candles = await client.app.advanced_trade.http.products.public.candles(
    'BTC-USD', start=now - 3600, end=now, granularity='ONE_HOUR',
  )
```

Others are RFC 3339 on the wire but take a real Python `datetime` in the signature — the
client renders it to the RFC 3339 string the venue expects:

```python
from datetime import datetime, timezone
from typed_coinbase import Coinbase

async with Coinbase.new() as client:
  fills = await client.app.advanced_trade.http.orders.historical.fills(
    start_sequence_timestamp=datetime(2024, 1, 1, tzinfo=timezone.utc),
    end_sequence_timestamp=datetime(2024, 1, 2, tzinfo=timezone.utc),
  )
```

Check the specific endpoint's signature: some request parameters take a raw UNIX `int`
(see above), others a real `datetime`, and none take a raw RFC 3339 `str` directly.
