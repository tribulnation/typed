"""Deribit-specific wire types: `TimestampMillis`/`TimestampNanos`, Deribit's millisecond-
and nanosecond-epoch UTC timestamp shapes, and `DateIso`, a plain calendar date, all
threaded through pydantic validation.

Deribit documents every `*timestamp*` response field (order/trade/instrument
`creation_timestamp`, `timestamp`, `expiration_timestamp`, ...) as milliseconds since the
Unix epoch, confirmed across the market-data and trading method references.

`starbase_timestamp`/`starbase_last_update_timestamp` are the one exception: Starbase's own
causal timestamps are nanosecond-epoch, confirmed from captured examples (19-digit values,
e.g. `1536569522277000000`). `get_delivery_prices`'s `date` field is a plain calendar date
with no time component (e.g. `"2026-08-03"`).
"""

from typing_extensions import Annotated
from datetime import date, datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import DateConverter, EpochConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)

TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""A millisecond-epoch UTC timestamp field, to use directly in a generated `TypedDict`'s
annotations."""

timestamp_nanos = EpochConverter.nanoseconds(tz=timezone.utc)

TimestampNanos = Annotated[
  datetime,
  BeforeValidator(timestamp_nanos.parse),
  PlainSerializer(timestamp_nanos.dump, when_used='json'),
]
"""A nanosecond-epoch UTC timestamp field (Starbase's own causal timestamps), to use
directly in a generated `TypedDict`'s annotations."""

date_iso = DateConverter()

DateIso = Annotated[
  date,
  BeforeValidator(date_iso.parse),
  PlainSerializer(date_iso.dump, when_used='json'),
]
"""A plain calendar date field with no time component, to use directly in a generated
`TypedDict`'s annotations."""
