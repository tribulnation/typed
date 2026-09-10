"""Kraken's wire timestamp shapes: RFC 3339 strings (e.g. `post_trade`'s `from_ts`/`to_ts`
and response fields like `last_ts`/`trade_ts`/`publication_ts`), UTC, plus Unix epoch
seconds elsewhere (e.g. `api_key_info`'s `createdTime`/`modifiedTime`, `ledgers`'s `time`).

A handful of fields carry nanosecond-precision epoch values instead (`order_amends`'s
`timestamp`, `market_data.trades`'s `since`/`last`) -- declared `epoch-nanos` and converted
here. See those endpoints' own `notes`.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import IsoConverter, EpochConverter

timestamp_iso = IsoConverter()
timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
timestamp_nanos = EpochConverter.nanoseconds(tz=timezone.utc)

TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""A `date-time` (RFC 3339) timestamp field, to use directly in a generated `TypedDict`'s
annotations."""
TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""An `epoch-seconds` timestamp field, to use directly in a generated `TypedDict`'s
annotations. Request-side (`spot.market_data.ohlc`/`spread`'s `since`), not just
response-side -- ADR 0020/S27's `PlainSerializer` is load-bearing here: without it,
`validator(Request).dump(...)` (the request-side serialization every generated `rpc`
method now goes through) would silently render `since` as an ISO-8601 string instead of
a Unix-second epoch."""
TimestampNanos = Annotated[
  datetime,
  BeforeValidator(timestamp_nanos.parse),
  PlainSerializer(timestamp_nanos.dump, when_used='json'),
]
"""An `epoch-nanos` timestamp field, to use directly in a generated `TypedDict`'s
annotations. Request-side (`spot.market_data.trades`'s `since`), same reasoning as
`TimestampSeconds` above."""
