from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from fractions import Fraction
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
        than a bare number (binance's `options.market.open_interest.timestamp`),
        others as a fractional number (kraken's `trades_history` `time`).
        Integer and string inputs avoid floating-point conversion. Submicrosecond
        values round to the nearest representable microsecond, with ties to even.

    Raises:
      ValueError: `value` is not a number or a numeral string (a JSON `null` on a
        non-nullable field), so pydantic reports it as a validation failure instead of
        a `TypeError` escaping the `BeforeValidator`.
    """
    if isinstance(value, bool) or not isinstance(value, int | float | str):
      raise ValueError(
        f'epoch timestamp must be a number or numeral string, got {type(value).__name__}'
      )
    try:
      numeric = Fraction(Decimal(value)) if isinstance(value, str) else Fraction(value)
    except InvalidOperation as error:
      raise ValueError('epoch timestamp must be a numeral string') from error
    microseconds = round(numeric * 1_000_000 / Fraction(self.unit))
    seconds, remainder = divmod(microseconds, 1_000_000)
    return datetime.fromtimestamp(seconds, self.tz).replace(microsecond=remainder)

  def dump(self, dt: datetime) -> int:
    """Convert a datetime to epoch units without floating-point timestamp loss.

    Fractional wire units truncate toward zero. Naive datetimes retain Python's
    existing local-time interpretation, just as datetime.timestamp() does.
    """
    delta = dt.astimezone(timezone.utc) - datetime(1970, 1, 1, tzinfo=timezone.utc)
    microseconds = (delta.days * 86400 + delta.seconds) * 1_000_000 + delta.microseconds
    return int(Fraction(microseconds) * Fraction(self.unit) / 1_000_000)

  def now(self) -> int:
    """The current time, in the unit specified."""
    return int(self.unit * time.time())
