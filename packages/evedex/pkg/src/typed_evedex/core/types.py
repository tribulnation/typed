"""EVEDEX wire timestamp types.

The venue uses two shapes: epoch milliseconds (`/api/ping`'s `time`, order-book `t`, candle
open times) and RFC 3339 strings (`createdAt`, `updatedAt`, candle-history bounds).
"""

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
"""An epoch-millisecond wire timestamp, as an aware UTC `datetime`."""


class MillisIsoConverter(IsoConverter):
  """RFC 3339 in the venue's own form: UTC, millisecond precision, `Z`-suffixed
  (`2026-11-19T11:20:51.255Z`). Sub-millisecond precision is truncated."""

  def dump(self, dt: datetime) -> str:
    """Render `dt` as `YYYY-MM-DDTHH:MM:SS.mmmZ` in UTC."""
    dt = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return dt.strftime('%Y-%m-%dT%H:%M:%S.') + f'{dt.microsecond // 1000:03d}Z'


timestamp_iso = MillisIsoConverter()
TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""An RFC 3339 wire timestamp (`2026-11-19T11:20:51.255Z`), as an aware UTC `datetime`."""


class SeekIsoConverter(MillisIsoConverter):
  """An RFC 3339 bound whose seek cursor is read off rows in another format.

  The candle history is bounded by RFC 3339 `after`/`before` (the venue refuses epoch
  numbers there, `invalid_date`) while its rows carry epoch-millisecond open times. A seek
  walk parses each row's key through the moving bound's converter, so this one also takes
  an epoch-millisecond number (a row read with validation off) or an already-parsed
  `datetime` (validation on), and dumps RFC 3339 like `timestamp_iso`.
  """

  def parse(self, value: str | int | datetime) -> datetime:  # type: ignore[override]
    """Parse an RFC 3339 string, an epoch-millisecond number or a `datetime`."""
    if isinstance(value, datetime):
      return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)
    if isinstance(value, str):
      return super().parse(value)
    return timestamp_millis.parse(int(value))


timestamp_seek_iso = SeekIsoConverter()
"""The candle walk's bound converter (`SeekIsoConverter`)."""
