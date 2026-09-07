from dataclasses import dataclass
from datetime import datetime, timezone
import time
from .base import TimeConverter

@dataclass(kw_only=True)
class EpochConverter(TimeConverter[int]):
  """Converter for epoch timestamps in a specific unit and timezone."""

  unit: float
  """Unit of the epoch timestamps, e.g. 1e3 for milliseconds, 1 for seconds."""
  tz: timezone | None = None
  """Timezone of the timestamps. If None, timestamps are naive."""

  @classmethod
  def milliseconds(cls, tz: timezone | None = None):
    """Create a converter for millisecond epoch timestamps."""
    return cls(unit=1e3, tz=tz)

  @classmethod
  def seconds(cls, tz: timezone | None = None):
    """Create a converter for second epoch timestamps."""
    return cls(unit=1, tz=tz)

  @classmethod
  def microseconds(cls, tz: timezone | None = None):
    """Create a converter for microsecond epoch timestamps."""
    return cls(unit=1e6, tz=tz)

  @classmethod
  def nanoseconds(cls, tz: timezone | None = None):
    """Create a converter for nanosecond epoch timestamps."""
    return cls(unit=1e9, tz=tz)

  def parse(self, value: int | float | str) -> datetime:
    """Parse an epoch timestamp into a `datetime`.

    Args:
      value: The epoch timestamp. Some venues serialize it as a numeral string rather
        than a bare number (binance's `options.market.open_interest.timestamp`,
        confirmed live: `"timestamp": "1786302600000"`), others as a fractional number
        (kraken's `trades_history` `time`: `1688669597.8277`); a string is parsed as an
        `int` when it can be, so a large integer keeps every digit, and as a `float`
        otherwise.

    Raises:
      ValueError: `value` is not a number or a numeral string (a JSON `null` on a
        non-nullable field), so pydantic reports it as a validation failure instead of
        a `TypeError` escaping the `BeforeValidator`.
    """
    if isinstance(value, bool) or not isinstance(value, int | float | str):
      raise ValueError(f'epoch timestamp must be a number or numeral string, got {type(value).__name__}')
    if isinstance(value, str):
      try:
        value = int(value)
      except ValueError:
        value = float(value)
    return datetime.fromtimestamp(value / self.unit, self.tz)

  def dump(self, dt: datetime) -> int:
    """Convert a `datetime` back into an epoch timestamp."""
    return int(self.unit * dt.timestamp())

  def now(self) -> int:
    """The current time, in the unit specified."""
    return int(self.unit * time.time())
