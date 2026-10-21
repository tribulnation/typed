"""Margin Trade wire timestamp types: epoch milliseconds almost everywhere (`depositHistory`'s
snake_case `created_at`/`last_updated` included), epoch seconds on the CoinGecko contracts'
`next_funding_rate_timestamp`, ISO 8601 strings on `/version` only.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import EpochConverter, IsoConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
"""Converter for epoch-millisecond fields (`time`, `ts`, `startTime`, `createTime`, ...)."""

TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""An epoch-millisecond field, as a UTC `datetime`."""

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
"""Converter for epoch-second fields (`next_funding_rate_timestamp`)."""

TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""An epoch-second field, as a UTC `datetime`."""

timestamp_iso = IsoConverter()
"""Converter for ISO 8601 string fields (`build_time`)."""

TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""An ISO 8601 string field, as a `datetime`."""
