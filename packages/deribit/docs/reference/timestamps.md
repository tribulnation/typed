# Timestamps

Deribit's own wire format is raw epoch integers everywhere, but the generated surface never
hands you one directly: every documented timestamp field and parameter — request and
response, across `.http`, `.ws`, and `.streams` — is a real Python `datetime`. Conversion
happens automatically through pydantic validation on the way in, and through the same
converter on the way out when a request is built for the wire.

Three types cover it, all importable from `typed_deribit.core`:

- `TimestampMillis` — millisecond-epoch UTC. This is the vast majority of Deribit's
  timestamp fields: order and trade `creation_timestamp`, `timestamp`, instrument
  `expiration_timestamp`, the `start_timestamp`/`end_timestamp` window bounds on
  market-data and account endpoints, and more.
- `TimestampNanos` — nanosecond-epoch UTC, used only for Starbase's own causal timestamps:
  `starbase_timestamp` (on trades) and `starbase_last_update_timestamp` (on orders).
- `DateIso` — a plain calendar date with no time component, used only for
  `get_delivery_prices`'s `date` field (e.g. `2026-08-03`).

All three are `Annotated` aliases over `datetime`/`date` — real types you can use in your
own code, not internal implementation details.

## Passing A Timestamp

A windowed request takes real `datetime` objects for its bounds:

```python
from datetime import datetime, timezone
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  history = await client.http.market_data.get_funding_rate_history(
    instrument_name='BTC-PERPETUAL',
    start_timestamp=datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc),
    end_timestamp=datetime(2023, 11, 14, 23, 13, 20, tzinfo=timezone.utc),
  )
```

A naive `datetime` (no `tzinfo`) works too — Deribit's converter treats it as UTC — but
passing an explicit `timezone.utc` reads clearest and avoids relying on that default.

## Reading A Timestamp

Response timestamp fields (`Ticker.timestamp`, `BookSummaryItem.creation_timestamp`, order
and trade timestamps, ...) come back as real `datetime` values, already converted:

```python
from typed_deribit import Deribit

async with Deribit.new(public=True) as client:
  ticker = await client.http.market_data.ticker(instrument_name='BTC-PERPETUAL')
  print(ticker['timestamp'], ticker['timestamp'].tzinfo)
```

## Starbase Nanosecond Fields

`starbase_timestamp`/`starbase_last_update_timestamp` (trade and order fields) are typed
`TimestampNanos` instead — same `datetime` shape, converted from a nanosecond-epoch wire
value rather than milliseconds. No special handling is needed on your side; the field just
carries more precision than every other timestamp in the client.

## Raw Helpers

`TimestampMillis`/`TimestampNanos`/`DateIso` are pydantic-validated type aliases, not
converter objects themselves. The converters behind them (`timestamp_millis`,
`timestamp_nanos`, `date_iso`) are also importable from `typed_deribit.core`, if you ever
need to convert a `datetime` to a raw epoch value by hand — for example, to compare against
a value read from somewhere outside the client:

```python
from datetime import datetime, timezone
from typed_deribit.core import timestamp_millis

now_ms = timestamp_millis.dump(datetime.now(timezone.utc))
as_datetime = timestamp_millis.parse(now_ms)
```
