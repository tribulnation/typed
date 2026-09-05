"""Bybit's wire timestamp shapes: Unix epoch milliseconds (the overwhelming majority of
fields), epoch seconds, and a handful of RFC 3339 strings.

Each pairs a `BeforeValidator` (response-side parsing) with a `PlainSerializer` (S27,
ADR 0020) -- load-bearing now that request bodies also go through
`validator(Request).dump(...)` (design §7): without the serializer, a `datetime`-typed
request field would render as an ISO-8601 string regardless of its real wire format.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import EpochConverter, IsoConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
timestamp_iso = IsoConverter()

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
