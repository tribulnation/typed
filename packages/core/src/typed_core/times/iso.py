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
  """Converter for RFC 3339 timestamps, `Z`-suffixed on the wire."""

  tz: timezone | None = timezone.utc
  """Timezone attached to a wire value that carries no offset of its own. Defaults to UTC,
  matching what `dump` already assumes of a naive `datetime`; `None` keeps such a value
  naive. A value carrying `Z` or an explicit offset is never touched."""

  def parse(self, value: str) -> datetime:
    """Parse a `Z`-suffixed, possibly non-microsecond-precision ISO 8601 timestamp.

    Args:
      value: The wire timestamp. `Z` is normalized to `+00:00` and the fractional
        part, if any, is padded or truncated to exactly 6 digits, so parsing behaves
        the same on every Python version this package supports -- both are 3.11+-only
        otherwise. An offset-free value gets `tz` attached.

    Raises:
      ValueError: `value` is not a string (a JSON `null` on a non-nullable field), so
        pydantic reports it as a validation failure instead of an `AttributeError`
        escaping the `BeforeValidator`.
    """
    if not isinstance(value, str):
      raise ValueError(f'ISO 8601 timestamp must be a string, got {type(value).__name__}')
    if value.endswith('Z'):
      value = value[:-1] + '+00:00'
    if m := _FRACTION.search(value):
      digits = (m.group(1) + '000000')[:6]
      value = value[:m.start(1)] + digits + value[m.end(1):]
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None and self.tz is not None:
      dt = dt.replace(tzinfo=self.tz)
    return dt

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
