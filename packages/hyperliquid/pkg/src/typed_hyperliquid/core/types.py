"""Hyperliquid's wire timestamps. `TimestampMillis` covers the venue's dominant shape,
milliseconds since the Unix epoch, UTC, threaded through nonce generation
(`timestamp_millis.now()`, used by every signed exchange action) and available for response
fields that adopt it instead of a bare `int`. `TimestampIso` covers the handful of fields
(deploy/HIP-3 config timestamps) that the venue instead renders as an ISO 8601 string.
`DateIso` covers the one field (`user_fees.dailyUserVlm[].date`) that is a plain calendar
date with no time component (e.g. `"2026-04-26"`).

Both timestamp types pair a `BeforeValidator` (wire -> `datetime`, on the way in) with a
`PlainSerializer` (`datetime` -> wire, on the way out) -- ADR 0020/S27, now load-bearing:
every generated `rpc_endpoint`/`stream_endpoint` call serializes its request through
`validator(request_type).dump(...)`, so a request-side timestamp field (nonce/expiry
overrides, `startTime`/`endTime` window bounds) needs the dump half to round-trip back to
the venue's real epoch-millis wire shape, not pydantic's ISO-8601 default. `DateIso` does
the same for `date` in and out of a plain `datetime.date`.
"""

from typing_extensions import Annotated
from datetime import date, datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import DateConverter, EpochConverter, IsoConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)

TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""A timestamp field, to use directly in a response or request `TypedDict`'s annotations."""

timestamp_iso = IsoConverter()

TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""An ISO 8601 timestamp field, to use directly in a response or request `TypedDict`'s
annotations."""

date_iso = DateConverter()

DateIso = Annotated[
  date,
  BeforeValidator(date_iso.parse),
  PlainSerializer(date_iso.dump, when_used='json'),
]
"""A plain calendar date field with no time component, to use directly in a response or
request `TypedDict`'s annotations."""
