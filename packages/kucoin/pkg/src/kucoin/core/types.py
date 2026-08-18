"""Venue-specific wire types: KuCoin's timestamp shape threaded through pydantic validation.

References:
  - [KuCoin API docs](https://www.kucoin.com/docs-new)
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator

from typed_core.times import EpochConverter

timestamp = EpochConverter.milliseconds(tz=timezone.utc)
"""Every KuCoin timestamp field is a millisecond Unix epoch integer, UTC — confirmed live
against `/api/v1/timestamp` (Spot and Futures) and `/api/v2/user-info`'s neighboring fields.
"""

Timestamp = Annotated[datetime, BeforeValidator(timestamp.parse)]
"""A timestamp field, to use directly in a generated `TypedDict`'s annotations."""
