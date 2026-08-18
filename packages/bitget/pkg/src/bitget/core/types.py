"""Bitget-specific wire types: `Timestamp`, the venue's epoch-millisecond timestamp shape."""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator

from typed_core.times import EpochConverter

timestamp = EpochConverter.milliseconds(tz=timezone.utc)


def _parse_timestamp(value: str | int) -> datetime:
  """Bitget sends epoch-millisecond timestamps as either a JSON number or a numeric
  string depending on the endpoint (e.g. `serverTime` is a string, WS `ts` is a number) —
  normalize both through the same `int()` before converting.
  """
  return timestamp.parse(int(value))


Timestamp = Annotated[datetime, BeforeValidator(_parse_timestamp)]
"""A Bitget epoch-millisecond timestamp field, to use directly in a `TypedDict`'s annotations."""
