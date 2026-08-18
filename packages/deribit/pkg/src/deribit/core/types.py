"""Deribit-specific wire types: `Timestamp`, Deribit's millisecond epoch UTC timestamp
shape, threaded through pydantic validation.

Deribit documents every `*timestamp*` response field (order/trade/instrument
`creation_timestamp`, `timestamp`, `expiration_timestamp`, ...) as milliseconds since the
Unix epoch, confirmed across the market-data and trading method references.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator

from typed_core.times import EpochConverter

timestamp = EpochConverter.milliseconds(tz=timezone.utc)

Timestamp = Annotated[datetime, BeforeValidator(timestamp.parse)]
"""A millisecond-epoch UTC timestamp field, to use directly in a generated `TypedDict`'s
annotations."""
