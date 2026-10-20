# Timestamps

Every timestamp is a timezone-aware UTC `datetime`, in requests and responses alike. The
client converts to and from the wire format, which is epoch milliseconds almost everywhere.

## Responses

```python
from typed_extended import Extended

async with Extended.new(public=True) as client:
  trades = await client.info.trades('BTC-USD')
  print(trades[0]['T'])  # datetime
  stats = await client.info.market_stats('BTC-USD')
  print(stats['nextFundingRate'])  # datetime
```

## Requests

Range parameters (`start_time`, `end_time`) take a `datetime` directly:

```python
from datetime import datetime, timedelta, timezone
from typed_extended import Extended

async with Extended.new(public=True) as client:
  end = datetime.now(timezone.utc)
  funding = await client.info.funding_rates(
    'BTC-USD', start_time=end - timedelta(hours=8), end_time=end
  )
```

An order's `expiryEpochMillis` is a `datetime` too, defaulting to one hour from now when
omitted.

## Other Units

A few fields use other wire formats; all of them still arrive as Python values:

- Settlement expirations on transfers and withdrawals are epoch seconds (`datetime`).
- Points epoch boundaries (`startDate`, `endDate`) are plain calendar dates (`date`); `endDate`
  is the epoch's last day, inclusive.
- Portfolio chart points and the builder dashboard use plain calendar dates (`date`).
