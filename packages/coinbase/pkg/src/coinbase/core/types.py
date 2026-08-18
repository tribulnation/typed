"""Coinbase's wire timestamp shape: ISO 8601, 'Z'-suffixed, with fractional-second
precision ranging from none up to nanoseconds (WebSocket payloads go to 9 digits).
`datetime` can't hold past microseconds and `datetime.fromisoformat` can't parse a `Z`
suffix before Python 3.11, so both are normalized before parsing.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator
import re

from typed_core.times.base import TimeConverter

_FRACTION = re.compile(r'\.(\d+)')


class CoinbaseIsoConverter(TimeConverter[str]):
  """Converter for Coinbase's `Z`-suffixed ISO 8601 timestamps."""

  def parse(self, value: str) -> datetime:
    """Parse a Coinbase wire timestamp into a `datetime`."""
    if value.endswith('Z'):
      value = value[:-1] + '+00:00'
    if (m := _FRACTION.search(value)) and len(m.group(1)) > 6:
      value = value[: m.start(1)] + m.group(1)[:6] + value[m.end(1) :]
    return datetime.fromisoformat(value)

  def dump(self, dt: datetime) -> str:
    """Convert a `datetime` back into a Coinbase wire timestamp."""
    return dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')

  def now(self) -> str:
    """The current time, in Coinbase's wire format."""
    return self.dump(datetime.now(timezone.utc))


timestamp = CoinbaseIsoConverter()

Timestamp = Annotated[datetime, BeforeValidator(timestamp.parse)]
"""A Coinbase wire timestamp field, to use directly in a generated `TypedDict`'s annotations."""
