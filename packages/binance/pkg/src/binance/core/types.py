"""Binance-specific wire types — starting with `Timestamp`, Binance's timestamp shape
threaded through pydantic validation.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator

from typed_core.times import EpochConverter

timestamp = EpochConverter.milliseconds(tz=timezone.utc)
"""Binance timestamps are millisecond epoch integers, UTC. `X-MBX-TIME-UNIT: MICROSECOND`
opts an account into microsecond timestamps instead — not handled here, since it's a
per-request header choice rather than a fixed wire shape.
"""

Timestamp = Annotated[datetime, BeforeValidator(timestamp.parse)]
"""A timestamp field, to use directly in a generated `TypedDict`'s annotations."""
