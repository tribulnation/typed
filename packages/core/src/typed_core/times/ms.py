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

  def parse(self, value: int | str) -> datetime:
    """Parse an epoch timestamp into a `datetime`.

    Args:
      value: The epoch timestamp. Some venues serialize it as a numeral string rather
        than a bare number (binance's `options.market.open_interest.timestamp`,
        confirmed live: `"timestamp": "1786302600000"`) -- coerced with `int()` first.
    """
    return datetime.fromtimestamp(int(value) / self.unit, self.tz)

  def dump(self, dt: datetime) -> int:
    """Convert a `datetime` back into an epoch timestamp."""
    return int(self.unit * dt.timestamp())

  def now(self) -> int:
    """The current time, in the unit specified."""
    return int(self.unit * time.time())
