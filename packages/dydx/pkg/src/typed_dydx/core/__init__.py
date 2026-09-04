"""Core dYdX exceptions and timestamp types."""

from datetime import datetime
from pydantic import BeforeValidator
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
from typed_core.times import IsoConverter

timestamp_iso = IsoConverter()
TimestampIso = Annotated[datetime, BeforeValidator(timestamp_iso.parse)]
"""RFC 3339 timestamp, as the Indexer's `date-time`-formatted fields carry it."""
