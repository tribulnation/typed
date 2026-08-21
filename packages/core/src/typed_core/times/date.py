from dataclasses import dataclass
from datetime import datetime
from .base import TimeConverter

@dataclass(kw_only=True)
class DateConverter(TimeConverter[str]):
  """Converter for a plain RFC 3339 full-date, with no time component (`YYYY-MM-DD`)."""

  def parse(self, value: str) -> datetime:
    """Parse a `YYYY-MM-DD` calendar date into a `datetime` at midnight.

    Args:
      value: The wire date, e.g. `'2026-08-03'`. Carries no time component, so the
        returned `datetime` is always naive and set to midnight.
    """
    return datetime.strptime(value, '%Y-%m-%d')

  def dump(self, dt: datetime) -> str:
    """Render a `datetime` back to `YYYY-MM-DD`, dropping any time component."""
    return dt.strftime('%Y-%m-%d')

  def now(self) -> str:
    """Today's date, in wire format."""
    return self.dump(datetime.now())
