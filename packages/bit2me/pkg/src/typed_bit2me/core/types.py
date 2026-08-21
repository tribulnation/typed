"""Bit2Me wire-type aliases."""

from datetime import datetime, timezone
from typing_extensions import Annotated
from pydantic import BeforeValidator

from typed_core.times import EpochConverter, IsoConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
"""Converts Bit2Me's Unix-epoch-milliseconds wire timestamps, per `MillisTimestamp`'s
`spec/schemas.json` description ("Time in Unix epoch time format") and every captured
example (e.g. `1713613906000`)."""

TimestampMillis = Annotated[datetime, BeforeValidator(timestamp_millis.parse)]
"""A timestamp field, to use directly in a generated TypedDict's annotations."""

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
"""Converts Bit2Me's Unix-epoch-seconds wire timestamps -- `TokenResponse.expirationTime`
(`v1.signin.embed`/`v1.signin.apikey`), confirmed by every recorded example carrying a
10-digit value (e.g. `1713613966`), an order of magnitude smaller than the 13-digit
millisecond values `timestamp_millis` converts elsewhere."""

TimestampSeconds = Annotated[datetime, BeforeValidator(timestamp_seconds.parse)]
"""A timestamp field, to use directly in a generated TypedDict's annotations."""

timestamp_iso = IsoConverter()
"""Converts Bit2Me's RFC 3339 wire timestamps (`startTime`/`endTime`/`time`/`from`/`to`),
confirmed live: a correctly-formatted value is accepted, `str(datetime)` gets a real
HTTP 400 `INVALID_FORMAT` (`.agents/handoff/bit2me-request-datetime-not-serialized.md`)."""

TimestampIso = Annotated[datetime, BeforeValidator(timestamp_iso.parse)]
"""A timestamp field, to use directly in a generated TypedDict's annotations."""
