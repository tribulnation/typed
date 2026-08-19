from dataclasses import dataclass
from datetime import datetime, timezone
import re
from .base import TimeConverter

_FRACTION = re.compile(r'\.(\d+)')
"""A wire fraction of any length -- some venues send milliseconds, others nanoseconds
(more digits than `datetime` can hold). Padding or truncating to exactly 6 digits
(microseconds) covers every wire length uniformly, and is one of only two forms
`datetime.fromisoformat` accepts before Python 3.11 (exactly 3 or 6 fractional digits;
this package targets `>=3.10`)."""

@dataclass(kw_only=True)
class IsoConverter(TimeConverter[str]):
  """Converter for RFC 3339 timestamps, always UTC and `Z`-suffixed on the wire."""

  def parse(self, value: str) -> datetime:
    """Parse a `Z`-suffixed, possibly non-microsecond-precision ISO 8601 timestamp.

    Args:
      value: The wire timestamp. `Z` is normalized to `+00:00` and the fractional
        part, if any, is padded or truncated to exactly 6 digits, so parsing behaves
        the same on every Python version this package supports -- both are 3.11+-only
        otherwise.
    """
    if value.endswith('Z'):
      value = value[:-1] + '+00:00'
    if m := _FRACTION.search(value):
      digits = (m.group(1) + '000000')[:6]
      value = value[:m.start(1)] + digits + value[m.end(1):]
    return datetime.fromisoformat(value)

  def dump(self, dt: datetime) -> str:
    """Convert a `datetime` to UTC and render it `Z`-suffixed.

    A naive `dt` is taken to already mean UTC -- its `tzinfo` is attached, not
    converted through, so serialization doesn't depend on the calling process's own
    local timezone. An aware `dt` in another offset is actually converted.
    """
    dt = dt.astimezone(timezone.utc) if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    return dt.isoformat().replace('+00:00', 'Z')

  def now(self) -> str:
    """The current time, in wire format."""
    return self.dump(datetime.now(timezone.utc))
