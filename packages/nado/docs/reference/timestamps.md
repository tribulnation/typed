# Timestamps

Every timestamp the client exposes is a timezone-aware UTC `datetime`, in requests and
responses alike. You never handle epoch numbers yourself.

Nado's wire format mixes units, and the client converts each field with its real unit:

| Where | Wire unit |
| --- | --- |
| Archive (indexer) data, order `expiration`, trigger order times, `latest_candlestick` | epoch seconds |
| Order nonces, edge `server_time`, the `all_bbo` stream | epoch milliseconds |
| Other stream events (`trade`, `fill`, `order_update`, ...), `market_liquidity` | epoch nanoseconds |
| `archive_v2.symbols` | RFC 3339 strings |

## In Requests

Pass a `datetime` wherever the API takes a time:

```python
from datetime import datetime, timedelta, timezone
from typed_nado import Nado

async with Nado.new(public=True) as client:
  candles = await client.archive.candlesticks(
    product_id=2,
    granularity=3600,
    max_time=datetime(2026, 11, 1, tzinfo=timezone.utc),  # sent as epoch seconds
    limit=24,
  )
```

An order's `expiration` is a `datetime` too:
`'expiration': datetime.now(timezone.utc) + timedelta(days=1)`.

Use aware `datetime`s (`tzinfo=timezone.utc`); a naive one is interpreted as local time.

## In Responses

```python
from typed_nado import Nado

async with Nado.new(public=True) as client:
  candles = await client.archive.candlesticks(product_id=2, granularity=60, limit=1)
  opened = candles['candlesticks'][0]['timestamp']
  print(opened.isoformat())
```

## Nonces

Order nonces embed an expiry time (`recv_time_ms << 20` plus random bits). The client
generates them; `Nado.new(recv_window=timedelta(seconds=...))` sets how far ahead that
time sits (90 s by default, at most 100 s). Requests arriving after it are discarded by
the venue.
