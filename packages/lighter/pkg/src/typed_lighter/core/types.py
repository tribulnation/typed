"""Lighter's wire timestamp types.

Lighter mixes units, all UTC:

- epoch milliseconds: most REST/WS times (trades, candles, range bounds, order and
  transaction expiries, transfers, RFQs);
- epoch microseconds: `transaction_time` (REST and WS) and the order book/ticker streams'
  `last_updated_at`;
- epoch seconds: order `timestamp`/`created_at`/`updated_at`, account, pool and
  announcement `created_at`, funding and PnL points, the `/` status `timestamp`, and
  auth-token expiries and deadlines;
- RFC 3339 strings: explorer times and notification `created_at`/`updated_at`;
- plain calendar dates (`historicalTradesExport`'s `date`): `YYYY-MM-DD`.
"""

from typing_extensions import Annotated
from datetime import date, datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import DateConverter, EpochConverter, IsoConverter

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""An epoch-seconds timestamp field."""

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

timestamp_iso = IsoConverter()
TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""An RFC 3339 timestamp field."""

date_iso = DateConverter()
DateIso = Annotated[
  date,
  BeforeValidator(date_iso.parse),
  PlainSerializer(date_iso.dump, when_used='json'),
]
"""A plain calendar date field, `YYYY-MM-DD` on the wire."""
