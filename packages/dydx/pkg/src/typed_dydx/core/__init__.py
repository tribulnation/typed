"""Core dYdX exceptions and timestamp types."""

from datetime import datetime, timezone
from pydantic import BeforeValidator, PlainSerializer
from typing_extensions import Annotated

from typed_core.exceptions import (
  ApiError,
  AuthError,
  BadRequest,
  Error,
  LogicError,
  NetworkError,
  RateLimited,
  ValidationError,
)
from typed_core.times import EpochConverter, IsoConverter

timestamp_iso = IsoConverter()
TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""RFC 3339 timestamp, as the Indexer's `date-time`-formatted fields carry it."""

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""Unix timestamp in (possibly fractional) seconds, as the Indexer's `epoch-seconds`-formatted
fields carry it (`GET /v4/time`'s `epoch`)."""
