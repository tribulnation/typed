"""gTrade's wire timestamp types: epoch milliseconds (Trading API, pricing), epoch
seconds (holding-rate history) and ISO 8601 strings (Backend Global history rows)."""

from typing_extensions import Annotated
from datetime import datetime, timezone

from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import EpochConverter, IsoConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""An epoch-milliseconds timestamp, as a UTC `datetime`."""

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""An epoch-seconds timestamp, as a UTC `datetime`."""

timestamp_iso = IsoConverter()
TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""An RFC 3339 timestamp, as a UTC `datetime`."""
