"""Hyperliquid's wire timestamp: milliseconds since the Unix epoch, UTC. Threaded through
nonce generation (`timestamp.now()`, used by every signed exchange action) and available
for response fields that adopt `Timestamp` instead of a bare `int`.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator

from typed_core.times import EpochConverter

timestamp = EpochConverter.milliseconds(tz=timezone.utc)

Timestamp = Annotated[datetime, BeforeValidator(timestamp.parse)]
"""A timestamp field, to use directly in a response `TypedDict`'s annotations."""
