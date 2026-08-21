"""Timestamp serialization helpers for indexer query parameters."""

from datetime import datetime


def dump(value: datetime) -> str:
  """Serialize a datetime for dYdX indexer query parameters.

  Args:
    value: Datetime to serialize.

  Returns:
    The parsed value.
  """
  return value.isoformat().replace('+00:00', 'Z')
