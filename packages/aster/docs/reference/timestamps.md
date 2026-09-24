# Timestamps

Every timestamp is a timezone-aware `datetime` in UTC, both in requests and in responses.
The client converts to and from Aster's wire units for you.

## Requests

Pass `datetime` values to any time parameter:

```python
from datetime import datetime, timedelta, timezone

from typed_aster import Aster

async with Aster.new(public=True) as client:
  end = datetime.now(timezone.utc)
  rates = await client.futures.market.funding_rate(
    'BTCUSDT', start_time=end - timedelta(days=3), end_time=end
  )
  print(rates[0]['fundingTime'])
```

## Responses

Response fields such as `time`, `updateTime` and `E` (event time) are `datetime` too. On the
wire, most are epoch milliseconds, while a few spot and prediction account fields are epoch
nanoseconds; both arrive as `datetime`.

## Durations And Nonces

Durations stay plain integers in milliseconds, for example `countdown_time` on
`client.futures.trade.countdown_cancel_all`. Request nonces are integers in epoch
microseconds (see [Place & Manage Orders](../how-to/place-and-manage-orders.md)).

## Raw Helpers

The converters behind these types are in `typed_aster.core`, for converting values yourself:

```python
from datetime import datetime, timezone

from typed_aster.core import timestamp_millis

millis = timestamp_millis.dump(datetime(2026, 9, 1, tzinfo=timezone.utc))
print(millis, timestamp_millis.parse(millis))
```
