# Timestamps

Every timestamp in Typed GRVT is a timezone-aware `datetime`, in requests and in validated
replies. The client converts to and from GRVT's wire formats.

## Wire Formats

| Where | On the wire | In Python |
| --- | --- | --- |
| Market data, trading and stream fields (`event_time`, `open_time`, `start_time`, ...) | unix **nanoseconds**, as a string | `datetime` (UTC) |
| `market.time()` | unix milliseconds | `datetime` (UTC) |
| Edge fields: `start_time`, `end_time` (`referral_epochs`), `create_time` (`investment_strategies`), `expires_at` (`bridge_withdrawal_quote`), `updated_at` (`bridge_withdrawal_status`) | ISO 8601 strings | `datetime` |

## Requests

Pass `datetime` values for time filters:

```python
from datetime import datetime, timedelta, timezone
from typed_grvt import Grvt

async with Grvt.new(public=True) as client:
  end = datetime.now(timezone.utc)
  trades = await client.market.trade_history(
    instrument='BTC_USDT_Perp', start_time=end - timedelta(hours=1), end_time=end
  )
  print(trades['result'][0]['event_time'])
```

Use aware datetimes (`timezone.utc`): a naive one is read as local time.

## Unset Timestamps

GRVT sends an unset nanosecond timestamp as `"0"`, so it reads as 1970-01-01 00:00 UTC
(epoch 0). The orders of a bulk create reply carry one in
`metadata.create_time` and `state.update_time`, since GRVT has not processed them yet.
Compare against epoch 0 to tell an unset time from a real one:

```python
from datetime import datetime, timezone
from typed_grvt.schemas import Order

UNSET = datetime(1970, 1, 1, tzinfo=timezone.utc)


def created_at(order: Order) -> datetime | None:
  """When GRVT received the order, or `None` if it has not processed it yet."""
  created = order['metadata'].get('create_time')
  return None if created is None or created == UNSET else created
```

## Unvalidated Replies

With `validate=False`, on a call or on `Grvt.new()`, a reply is returned exactly as GRVT sent
it: timestamps keep their wire format (nanosecond strings, milliseconds, ISO 8601 strings) and
are not converted to `datetime`. Requests still take `datetime` values, and
`timestamp_nanos` (below) converts a nanosecond string by hand.

## Precision

Python's `datetime` stops at microseconds, so the last three digits of a nanosecond
timestamp are dropped, and two GRVT events within the same microsecond get equal
`datetime` values. Sorting by time alone cannot order them.

## Raw Helpers

`typed_grvt.core.types.timestamp_nanos` converts nanosecond values by hand, for example
when building a pre-signed payload:

```python
from datetime import datetime, timezone
from typed_grvt.core.types import timestamp_nanos

wire = timestamp_nanos.dump(datetime(2026, 1, 1, tzinfo=timezone.utc))
print(wire, timestamp_nanos.parse(wire))
```
