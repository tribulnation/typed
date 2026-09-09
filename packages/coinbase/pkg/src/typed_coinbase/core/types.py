"""Coinbase's wire timestamp shapes.

`app`'s and `exchange`'s REST/WS timestamps use ISO 8601/RFC 3339 with up to
nanosecond fractional precision. The shared `typed_core.times.IsoConverter` handles that
wire shape and serializes request-body timestamps back to JSON.

`exchange`'s `products.candles` is the one endpoint spec'd with a second format,
`epoch-seconds` (each candle row's own bucket-start time) -- a plain Unix-second epoch, so
it reuses `typed_core.times.EpochConverter` directly rather than a bespoke converter, per
`.agents/skills/client-core`'s "Timestamp Types" standard shape.

`app.accounts.prices.spot`'s `date` query parameter is a third shape: a plain `YYYY-MM-DD`
calendar date with no time component, matching `typed_core.times.DateConverter`'s default
pattern exactly, so it's used directly rather than a bespoke converter.
"""

from typing_extensions import Annotated
from datetime import date, datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import DateConverter, EpochConverter, IsoConverter

timestamp_iso = IsoConverter()

TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""A Coinbase wire timestamp field, to use directly in a generated `TypedDict`'s annotations."""

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)

TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""A Coinbase Exchange Unix-second epoch timestamp field (`exchange.http.products.candles`'
row bucket-start time), to use directly in a generated `TypedDict`'s annotations."""

date_iso = DateConverter()

DateIso = Annotated[
  date,
  BeforeValidator(date_iso.parse),
  PlainSerializer(date_iso.dump, when_used='json'),
]
"""A Coinbase wire plain calendar date field (`app.accounts.prices.spot`'s `date` query
parameter), to use directly in a generated `TypedDict`'s annotations."""
