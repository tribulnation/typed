"""GRVT wire types: the timestamp shapes the venue sends.

- Gateway RPCs and streams send unix **nanoseconds** as JSON strings (`"1792409155217411286"`).
- `GET /time` sends unix **milliseconds** as a JSON number.
- Edge referral and bridge endpoints send ISO 8601 strings.
"""

from datetime import datetime, timezone
import time

from pydantic import BeforeValidator, PlainSerializer
from typing_extensions import Annotated

from typed_core.times import EpochConverter, IsoConverter, TimeConverter


class NanosecondsConverter(TimeConverter[str]):
  """Unix nanoseconds carried as a numeral string, both directions.

  `EpochConverter.nanoseconds` parses the string but dumps an `int`; GRVT encodes every
  64-bit integer as a JSON string, so a request timestamp must dump back to one.
  `datetime` holds microseconds, so the last three digits are dropped on parse.
  """

  epoch = EpochConverter.nanoseconds(tz=timezone.utc)

  def parse(self, value: str | int) -> datetime:
    """Parse a nanosecond timestamp, as a numeral string or a number."""
    return self.epoch.parse(value)

  def dump(self, dt: datetime) -> str:
    """Render a `datetime` as a nanosecond numeral string."""
    return str(self.epoch.dump(dt))

  def now(self) -> str:
    """The current time, as a nanosecond numeral string."""
    return str(time.time_ns())


timestamp_nanos = NanosecondsConverter()
TimestampNanos = Annotated[
  datetime,
  BeforeValidator(timestamp_nanos.parse),
  PlainSerializer(timestamp_nanos.dump, when_used='json'),
]
"""A gateway timestamp: unix nanoseconds as a string on the wire (`epoch-nanos`)."""

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""A millisecond timestamp, as a JSON number (`epoch-millis`; `GET /time`)."""

timestamp_iso = IsoConverter()
TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""An RFC 3339 timestamp (`date-time`; edge referral and bridge endpoints)."""
