"""Alchemy's wire timestamp shapes.

NFT metadata timestamps (`timeLastUpdated`, `lastIngestedAt`, an NFT mint's own
`timestamp`) are epoch milliseconds; Prices API timestamps (`lastUpdatedAt`) are RFC 3339
strings; Prices' historical-price window bounds (`startTime`/`endTime`) are epoch
seconds. All three shapes appear across the client's endpoints, so all three pairs are
defined here rather than picking one. The client's original core
(`core/util/timestamps.py`, retired) conflated them into a single `timestamp.parse` with
a string-fallback, which worked but obscured which shape a given field actually is on
the wire; codegen needs them kept apart, since a declared `format` resolves to exactly
one of these pairs (`docs/spec/authoring.md` rule 3).
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import EpochConverter, IsoConverter

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""An epoch-seconds field, e.g. Prices API's `startTime`/`endTime` window bounds."""

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""An epoch-milliseconds field, e.g. NFT API's `timeLastUpdated`."""

timestamp_iso = IsoConverter()
TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""An RFC 3339 string field, e.g. Prices API's `lastUpdatedAt`."""
