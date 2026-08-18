"""Kraken's wire timestamp shape: Unix seconds, sometimes fractional (e.g. trade
timestamps carry sub-second precision), UTC.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator

from typed_core.times import EpochConverter

timestamp = EpochConverter.seconds(tz=timezone.utc)

Timestamp = Annotated[datetime, BeforeValidator(timestamp.parse)]
"""A timestamp field, to use directly in a generated `TypedDict`'s annotations."""
