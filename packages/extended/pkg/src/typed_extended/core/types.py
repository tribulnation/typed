"""Extended's wire timestamp types.

Extended mixes units, all UTC:

- epoch milliseconds: almost everything (`T`, `ts`, `createdTime`, `updatedTime`,
  `expiryEpochMillis`, `nextFundingRate`, assets' `createdAt`, range bounds);
- epoch seconds: settlement expirations (`expiration.seconds`, `expirationTimestamp`);
- plain calendar dates (`YYYY-MM-DD`): portfolio chart points, the builder dashboard and
  points epochs' `startDate`/`endDate`.

No field is an RFC 3339 timestamp today; `TimestampIso` stays for `format: date-time`.
"""

from typing_extensions import Annotated
from datetime import date, datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import DateConverter, EpochConverter, IsoConverter

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""An epoch-seconds timestamp field."""

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""An epoch-milliseconds timestamp field."""

timestamp_iso = IsoConverter()
TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""An RFC 3339 timestamp field."""

date_iso = DateConverter()
DateIso = Annotated[
  date,
  BeforeValidator(date_iso.parse),
  PlainSerializer(date_iso.dump, when_used='json'),
]
"""A plain calendar date field, `YYYY-MM-DD` on the wire."""
