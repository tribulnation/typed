from dataclasses import dataclass
from datetime import date, datetime

@dataclass(kw_only=True)
class DateConverter:
  """Converter for a plain calendar date, with no time component.

  Not a `TimeConverter` -- that base class's contract is fixed to `datetime` (see
  `base.py`), and a calendar date has no time-of-day to round-trip through one. Widening
  `TimeConverter` itself to cover this would ripple its return type into every existing
  subclass for the sake of this one converter; standing alone keeps the blast radius to
  just this file.
  """

  pattern: str = '%Y-%m-%d'
  """`datetime.strptime`/`strftime` directive for the wire string, e.g. `'%Y%m%d'` for a
  compact `YYYYMMDD` date with no separators (bitget's broker-commission endpoints:
  `"date": "20260101"`). Defaults to RFC 3339's `YYYY-MM-DD`, matching every calendar
  date confirmed so far other than that one. Generic on the pattern the same way
  `EpochConverter` is generic on `unit`/`tz` -- a venue's exact wire encoding is a detail
  each client's own `core_package` supplies, not something this converter should special-
  case per format.
  """

  def parse(self, value: str) -> date:
    """Parse a wire calendar date.

    Args:
      value: The wire date, e.g. `'2026-08-03'` for the default pattern.
    """
    return datetime.strptime(value, self.pattern).date()

  def dump(self, d: date) -> str:
    """Render a `date` back to the wire pattern."""
    return d.strftime(self.pattern)

  def now(self) -> date:
    """Today's date."""
    return date.today()
