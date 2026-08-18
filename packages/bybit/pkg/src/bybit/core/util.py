"""Timestamp helpers for Bybit's millisecond epoch values."""

import time
from datetime import datetime


class timestamp:
  """Convert between Bybit millisecond epochs and `datetime`."""

  @staticmethod
  def parse(time: int | str | datetime) -> datetime:
    """Parse a Bybit millisecond epoch into a `datetime`."""
    return (
      time if isinstance(time, datetime) else datetime.fromtimestamp(int(time) / 1e3)
    )

  @staticmethod
  def dump(dt: datetime | int) -> int:
    """Serialize a `datetime` into a Bybit millisecond epoch."""
    return int(1e3 * dt.timestamp()) if isinstance(dt, datetime) else dt

  @staticmethod
  def now() -> int:
    """Current time as a Bybit millisecond epoch."""
    return int(time.time() * 1e3)
