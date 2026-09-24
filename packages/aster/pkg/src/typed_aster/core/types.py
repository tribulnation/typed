"""Aster's wire timestamp types, threaded through pydantic validation.

Futures, chain REST and the chain JSON-RPC use epoch milliseconds. Spot and prediction
report some account fields (`account.updateTime`) in epoch nanoseconds, and request
nonces are epoch microseconds, so all three units are exported.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import EpochConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""An epoch-milliseconds timestamp field."""

timestamp_micros = EpochConverter.microseconds(tz=timezone.utc)
TimestampMicros = Annotated[
  datetime,
  BeforeValidator(timestamp_micros.parse),
  PlainSerializer(timestamp_micros.dump, when_used='json'),
]
"""An epoch-microseconds timestamp field."""

timestamp_nanos = EpochConverter.nanoseconds(tz=timezone.utc)
TimestampNanos = Annotated[
  datetime,
  BeforeValidator(timestamp_nanos.parse),
  PlainSerializer(timestamp_nanos.dump, when_used='json'),
]
"""An epoch-nanoseconds timestamp field."""
