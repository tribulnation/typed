"""Nado's wire timestamp types.

Besides the timestamps, `IntegerString`/`BooleanString` are the request-side wire forms of
numbers and flags the venue only accepts as strings.

Nado mixes three epoch units, all UTC, usually sent as numeral strings:

- epoch seconds: archive (indexer) data (`timestamp`), order `expiration`, trigger
  `max_update_time` and `placed_at`/`updated_at` (measured; the docs say milliseconds), the
  `latest_candlestick` event's `timestamp` and the `funding_payment` event's `dt`;
- epoch milliseconds: nonces' and `recvTime`'s time part, `StreamAuthentication.expiration`,
  edge `server_time`, the `all_bbo` stream's `time`;
- epoch nanoseconds: subscription event `timestamp`s (`1794853618815276000`);
- RFC 3339 strings: the archive v2 `symbols` listing.
"""

from typing_extensions import Annotated, Callable
from datetime import datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import EpochConverter, IsoConverter

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""An epoch-seconds timestamp field."""

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""An epoch-milliseconds timestamp field."""

timestamp_nanos = EpochConverter.nanoseconds(tz=timezone.utc)
TimestampNanos = Annotated[
  datetime,
  BeforeValidator(timestamp_nanos.parse),
  PlainSerializer(timestamp_nanos.dump, when_used='json'),
]
"""An epoch-nanoseconds timestamp field."""

timestamp_iso = IsoConverter(tz=timezone.utc)
TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""An RFC 3339 timestamp field."""


def numeral(dump: Callable[[datetime], int]) -> Callable[[datetime], str]:
  """An epoch converter's `dump`, returning the numeral string instead of the number."""
  return lambda value: str(dump(value))


TimestampSecondsString = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(numeral(timestamp_seconds.dump), when_used='json'),
]
"""An epoch-seconds timestamp the venue carries as a numeral string."""

TimestampMillisString = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(numeral(timestamp_millis.dump), when_used='json'),
]
"""An epoch-milliseconds timestamp the venue carries as a numeral string (`ping`'s
`client_time`: a JSON number is refused with HTTP 422)."""

TimestampNanosString = Annotated[
  datetime,
  BeforeValidator(timestamp_nanos.parse),
  PlainSerializer(numeral(timestamp_nanos.dump), when_used='json'),
]
"""An epoch-nanoseconds timestamp the venue carries as a numeral string."""


def boolean_string(value: bool) -> str:
  """A boolean as the venue's `"true"`/`"false"` string."""
  return 'true' if value else 'false'


IntegerString = Annotated[int, PlainSerializer(str, when_used='json')]
"""An integer the venue only accepts as a numeral string (`"64900000000000000000000"`):
x18 prices and amounts, nonces, `ping.client_time`. Sending it as a JSON number is refused
with HTTP 422, so it always dumps as a string; responses parse either form."""

BooleanString = Annotated[bool, PlainSerializer(boolean_string, when_used='json')]
"""A flag the venue only accepts as the string `"true"`/`"false"` (`spot_leverage`,
`reduce_only` on `max_order_size`, ...). A JSON boolean is refused with HTTP 422, so it
always dumps as a string; responses parse either form."""
