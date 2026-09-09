"""Bybit's wire timestamp shapes: Unix epoch milliseconds (the overwhelming majority of
fields), epoch seconds, a handful of RFC 3339 (space-separated, UTC) strings, and
`DateIso`, a plain calendar date -- the affiliate endpoints' `startDate`/`endDate`/
`registerTime` request and response fields (`YYYY-MM-DD`, e.g. `affiliate.user_list`'s
`registerTime`).

Each pairs a `BeforeValidator` (response-side parsing) with a `PlainSerializer` (S27,
ADR 0020) -- load-bearing now that request bodies also go through
`validator(Request).dump(...)` (design §7): without the serializer, a `datetime`-typed
request field would render as an ISO-8601 string regardless of its real wire format.
"""

from typing_extensions import Annotated
from datetime import date, datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import DateConverter, EpochConverter, IsoConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
timestamp_iso = IsoConverter()
date_iso = DateConverter()

TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""An `epoch-millis` timestamp field -- Bybit's most common wire shape, request- and
response-side alike."""

TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""An `epoch-seconds` timestamp field."""

TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""A `date-time` (RFC 3339) timestamp field."""

DateIso = Annotated[
  date,
  BeforeValidator(date_iso.parse),
  PlainSerializer(date_iso.dump, when_used='json'),
]
"""A plain calendar date field with no time component."""
