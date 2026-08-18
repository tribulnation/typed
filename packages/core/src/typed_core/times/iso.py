from dataclasses import dataclass
from datetime import datetime
from .base import TimeConverter

@dataclass(kw_only=True)
class IsoConverter(TimeConverter[str]):
  """Converter for ISO 8601 formatted timestamps."""

  def parse(self, value: str) -> datetime:
    """Parse an ISO 8601 formatted timestamp into a `datetime`."""
    return datetime.fromisoformat(value)

  def dump(self, dt: datetime) -> str:
    """Convert a `datetime` back into an ISO 8601 formatted timestamp."""
    return dt.isoformat()

  def now(self) -> str:
    """The current time, in the unit specified."""
    return datetime.now().isoformat()
