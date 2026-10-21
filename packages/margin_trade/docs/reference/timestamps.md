# Timestamps

Margin Trade sends timestamps as epoch milliseconds almost everywhere. The client converts
them both ways, so you only handle `datetime`.

## Responses

Every timestamp field in a response is a timezone-aware UTC `datetime`:

```python
from typed_margin_trade import MarginTrade

async with MarginTrade.new(public=True) as client:
  book = await client.info.l2_book('BTC')
  print(book['time'].isoformat())  # e.g. 2026-10-21T09:30:00.123000+00:00
```

The one exception on the wire is `public.version()`, whose `build_time` is an ISO 8601
string; it is parsed to a `datetime` too.

## Requests

Time parameters (`start_time`, `end_time`, `startTime` in a request dict, `expires_at`)
take a `datetime` and are sent as epoch milliseconds:

```python
from datetime import datetime, timedelta, timezone
from typed_margin_trade import MarginTrade

address = '6dm8b7h4rPVuYTDzeo9uZQNRhKagAYBPBniCHiY7Dggx'

async with MarginTrade.new(public=True, mainnet=False) as client:
  end = datetime.now(timezone.utc)
  fills = await client.info.user_fills_by_time(address, start_time=end - timedelta(hours=6), end_time=end)
```

Pass timezone-aware datetimes. A naive `datetime` is interpreted in your machine's local
time zone.

## Raw Helpers

To convert epoch milliseconds yourself, use the client's converter:

```python
from datetime import datetime, timezone
from typed_margin_trade.core import timestamp_millis

dt = timestamp_millis.parse(1792540800000)  # -> datetime in UTC
ms = timestamp_millis.dump(datetime(2026, 10, 21, tzinfo=timezone.utc))  # -> int
```
