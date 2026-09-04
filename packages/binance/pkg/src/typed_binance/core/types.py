"""Binance-specific wire types — `TimestampMillis` for Binance's near-universal millisecond
epoch shape, and `TimestampIso` for the handful of endpoints (Prediction, some withdraw
histories) that instead send an RFC 3339/ISO 8601 timestamp string — threaded through
pydantic validation.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import EpochConverter, IsoConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
"""Binance timestamps are millisecond epoch integers, UTC. `X-MBX-TIME-UNIT: MICROSECOND`
opts an account into microsecond timestamps instead — not handled here, since it's a
per-request header choice rather than a fixed wire shape.
"""

TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""A timestamp field, to use directly in a generated `TypedDict`'s annotations.

Request-side (`spot.market.klines`'s `startTime`/`endTime`, and every other window-
paginated endpoint), not just response-side -- ADR 0020/S27's `PlainSerializer` is
load-bearing here: without it, `validator(Request).dump(...)` (the request-side
serialization every generated `rpc`/`ws_rpc` method now goes through, per the codegen-
mechanization migration) would silently render a `startTime`/`endTime` `datetime` as an
ISO-8601 string instead of the millisecond epoch integer Binance's wire actually expects.
"""

timestamp_iso = IsoConverter()
"""A minority of endpoints send an RFC 3339/ISO 8601 timestamp string instead of a
millisecond epoch integer -- Prediction's transfer/order timestamps (`2026-05-25T04:00:00.
000+00:00`), and the `YYYY-MM-DD[ HH:MM:SS]`-shaped fields on withdraw-history and
fund-NAV-history endpoints, which `datetime.fromisoformat` also parses cleanly."""

TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""An ISO-8601-string timestamp field, to use directly in a generated `TypedDict`'s
annotations. Request-side too, same reasoning as `TimestampMillis` above."""
