"""RISEx wire timestamp types.

RISEx mixes units, all UTC:

- epoch nanoseconds, sent as numeral strings: the documented default ("all time fields are
  in nanoseconds unless explicitly defined otherwise"), e.g. trade `time`, order
  `created_at`, funding `block_time`, candle `time`, WebSocket `worker_timestamp`, and the
  candle range bounds `from`/`to`;
- epoch seconds: permit and login `deadline`, signer `expiration`, competitions'
  `start_time`/`end_time`, points epochs, the WebSocket `oracle` channel's `timestamp`;
- RFC 3339 strings: the affiliate and fee-tier endpoints' dates (`format: date-time`).
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import EpochConverter, IsoConverter

timestamp_nanos = EpochConverter.nanoseconds(tz=timezone.utc)
TimestampNanos = Annotated[
  datetime,
  BeforeValidator(timestamp_nanos.parse),
  PlainSerializer(timestamp_nanos.dump, when_used='json'),
]
"""An epoch-nanoseconds timestamp field."""

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""An epoch-seconds timestamp field."""

timestamp_iso = IsoConverter()
TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""An RFC 3339 timestamp field."""
