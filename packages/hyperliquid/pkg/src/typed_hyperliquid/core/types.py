"""Hyperliquid's wire timestamps. `TimestampMillis` covers the venue's dominant shape,
milliseconds since the Unix epoch, UTC, threaded through nonce generation
(`timestamp_millis.now()`, used by every signed exchange action) and available for response
fields that adopt it instead of a bare `int`. `TimestampIso` covers the handful of fields
(deploy/HIP-3 config timestamps) that the venue instead renders as an ISO 8601 string.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator

from typed_core.times import EpochConverter, IsoConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)

TimestampMillis = Annotated[datetime, BeforeValidator(timestamp_millis.parse)]
"""A timestamp field, to use directly in a response `TypedDict`'s annotations."""

timestamp_iso = IsoConverter()

TimestampIso = Annotated[datetime, BeforeValidator(timestamp_iso.parse)]
"""An ISO 8601 timestamp field, to use directly in a response `TypedDict`'s annotations."""
