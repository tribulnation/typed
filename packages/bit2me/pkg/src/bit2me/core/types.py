"""Bit2Me wire-type aliases."""

from datetime import datetime, timezone
from typing_extensions import Annotated
from pydantic import BeforeValidator

from typed_core.times import EpochConverter

timestamp = EpochConverter.milliseconds(tz=timezone.utc)
"""Converts Bit2Me's Unix-epoch-milliseconds wire timestamps, per `MillisTimestamp`'s
`spec/schemas.json` description ("Time in Unix epoch time format") and every captured
example (e.g. `1713613906000`)."""

Timestamp = Annotated[datetime, BeforeValidator(timestamp.parse)]
"""A timestamp field, to use directly in a generated TypedDict's annotations."""
