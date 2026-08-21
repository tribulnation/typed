"""Kraken's wire timestamp shapes: RFC 3339 strings (e.g. `post_trade`'s `from_ts`/`to_ts`
and response fields like `last_ts`/`trade_ts`/`publication_ts`), UTC, plus Unix epoch
seconds elsewhere (e.g. `api_key_info`'s `createdTime`/`modifiedTime`, `ledgers`'s `time`).

A handful of fields carry nanosecond-precision epoch values instead (`order_amends`'s
`timestamp`, `market_data.trades`'s `since`/`last`) -- declared `epoch-nanos` and converted
here. See those endpoints' own `notes`.
"""

from typing_extensions import Annotated
from datetime import datetime
from pydantic import BeforeValidator

from typed_core.times import IsoConverter, EpochConverter

timestamp_iso = IsoConverter()
timestamp_seconds = EpochConverter.seconds()
timestamp_nanos = EpochConverter.nanoseconds()

TimestampIso = Annotated[datetime, BeforeValidator(timestamp_iso.parse)]
"""A `date-time` (RFC 3339) timestamp field, to use directly in a generated `TypedDict`'s
annotations."""
TimestampSeconds = Annotated[datetime, BeforeValidator(timestamp_seconds.parse)]
"""An `epoch-seconds` timestamp field, to use directly in a generated `TypedDict`'s
annotations."""
TimestampNanos = Annotated[datetime, BeforeValidator(timestamp_nanos.parse)]
"""An `epoch-nanos` timestamp field, to use directly in a generated `TypedDict`'s
annotations."""
