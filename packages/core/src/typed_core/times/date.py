from dataclasses import dataclass
from datetime import date, datetime

@dataclass(kw_only=True)
class DateConverter:
  """Converter for a plain RFC 3339 full-date, with no time component (`YYYY-MM-DD`).

  Not a `TimeConverter` -- that base class's contract is fixed to `datetime` (see
  `base.py`), and a calendar date has no time-of-day to round-trip through one. Widening
  `TimeConverter` itself to cover this would ripple its return type into every existing
  subclass for the sake of this one converter; standing alone keeps the blast radius to
  just this file.
  """

  def parse(self, value: str) -> date:
    """Parse a `YYYY-MM-DD` calendar date.

    Args:
      value: The wire date, e.g. `'2026-08-03'`.
    """
    return datetime.strptime(value, '%Y-%m-%d').date()

  def dump(self, d: date) -> str:
    """Render a `date` back to `YYYY-MM-DD`."""
    return d.strftime('%Y-%m-%d')

  def now(self) -> date:
    """Today's date."""
    return date.today()
