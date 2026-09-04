"""Bit2Me wire-type aliases.

Every type pairs its `BeforeValidator` (response-side parsing) with a matching
`PlainSerializer(..., when_used='json')` (ADR 0020/S27) -- load-bearing now that a
generated `rpc` endpoint's request body serializes through `validator(Request).dump(...)`
(design §7/ADR 0020/S28): `v1.trading.candles`' `startTime`/`endTime` are `epoch-millis`
request parameters, not just response fields, so without the serializer they'd silently
render as ISO-8601 strings instead of millisecond epoch integers on the wire.
"""

from datetime import date, datetime, timezone
from typing_extensions import Annotated
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import DateConverter, EpochConverter, IsoConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
"""Converts Bit2Me's Unix-epoch-milliseconds wire timestamps, per `MillisTimestamp`'s
`spec/schemas.json` description ("Time in Unix epoch time format") and every captured
example (e.g. `1713613906000`)."""

TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""A timestamp field, to use directly in a generated TypedDict's annotations.
Request-side (`v1.trading.candles`' `startTime`/`endTime`), not just response-side."""

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
"""Converts Bit2Me's Unix-epoch-seconds wire timestamps -- `TokenResponse.expirationTime`
(`v1.signin.embed`/`v1.signin.apikey`), confirmed by every recorded example carrying a
10-digit value (e.g. `1713613966`), an order of magnitude smaller than the 13-digit
millisecond values `timestamp_millis` converts elsewhere."""

TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""A timestamp field, to use directly in a generated TypedDict's annotations."""

timestamp_iso = IsoConverter()
"""Converts Bit2Me's RFC 3339 wire timestamps (`startTime`/`endTime`/`time`/`from`/`to`),
confirmed live: a correctly-formatted value is accepted, `str(datetime)` gets a real
HTTP 400 `INVALID_FORMAT` (`.agents/handoff/bit2me-request-datetime-not-serialized.md`)."""

TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""A timestamp field, to use directly in a generated TypedDict's annotations.
Request-side (`v1.trading.orders.list`/`v1.trading.trades.list`'s `startTime`/`endTime`,
`v1.wallet.transactions.list`'s `from`/`to`), not just response-side -- ADR 0020/S27's
`PlainSerializer` is load-bearing here: without it, `validator(Request).dump(...)` (the
request-side serialization every generated `rpc` method now goes through) would silently
render these as the wrong-precision default ISO-8601 instead of round-tripping through
`IsoConverter.dump`."""

date_iso = DateConverter()
"""Converts Bit2Me's plain calendar-date wire fields (`v2.currency.assets`' `createdAt`,
`v3.account`'s `birthDate`) -- no time-of-day component to round-trip, unlike
`timestamp_iso` above."""

DateIso = Annotated[
  date,
  BeforeValidator(date_iso.parse),
  PlainSerializer(date_iso.dump, when_used='json'),
]
"""A plain calendar-date field, to use directly in a generated TypedDict's annotations."""
