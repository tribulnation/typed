"""Gate DEX wire timestamp types, threaded through pydantic validation.

The unit is per action, not per venue: epoch milliseconds, epoch seconds and RFC 3339
strings all occur. Each pair below is the type a generated `TypedDict` field uses plus the
converter backing it.
"""

from typing_extensions import Annotated
from datetime import datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import EpochConverter, IsoConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
"""UTC-aware epoch-milliseconds converter backing `TimestampMillis`."""
TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""Epoch milliseconds: the `X-Timestamp` signing header (`timestamp_millis.now()`). No
response or request field uses this unit; `market.price`'s `time` is epoch seconds."""

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
"""UTC-aware epoch-seconds converter backing `TimestampSeconds`."""
TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""Epoch seconds: `market.price`'s `time` (a numeral string), candle `ts`,
`trade.swap.build`'s `ts`, `base.token.get_trade_info`'s `price_update_ts`,
`base.token.ranking`'s `risk_info_update_ts`, the liquidity events' `block_timestamp`,
`market.volume_stats`'s `timestamp`, and `market.candles`'s `start`/`end` request bounds."""

timestamp_iso = IsoConverter()
"""RFC 3339 converter backing `TimestampIso`."""
TimestampIso = Annotated[
  datetime,
  BeforeValidator(timestamp_iso.parse),
  PlainSerializer(timestamp_iso.dump, when_used='json'),
]
"""RFC 3339: `base.token.range_by_created_at`'s `start`/`end` and its tokens'
`created_at`/`updated_at`, and the order record's `creationTime`/`endTime`."""
