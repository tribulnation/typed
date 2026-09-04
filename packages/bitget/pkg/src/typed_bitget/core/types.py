"""Bitget-specific wire types: `TimestampMillis`, the venue's epoch-millisecond timestamp
shape, and `DateIso`, its broker-commission endpoints' compact calendar-date shape.

Each pairs a `BeforeValidator` (response-side parsing) with a `PlainSerializer` (S27,
ADR 0020) -- load-bearing now that request bodies also go through
`validator(Request).dump(...)` (design §7): without the serializer, a `datetime`/`date`
-typed request field would render as an ISO-8601 string regardless of its real wire
format.
"""

from typing_extensions import Annotated
from datetime import date, datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import DateConverter, EpochConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)

TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""A Bitget epoch-millisecond timestamp field, to use directly in a `TypedDict`'s annotations.

Bitget sends epoch-millisecond timestamps as either a JSON number or a numeric string
depending on the endpoint (e.g. `serverTime` is a string, WS `ts` is a number) —
`EpochConverter.parse` coerces both through `int()` before converting, so this is
invisible from the caller's side.
"""

date_compact = DateConverter(pattern='%Y%m%d')

DateIso = Annotated[
  date, BeforeValidator(date_compact.parse), PlainSerializer(date_compact.dump, when_used='json'),
]
"""A Bitget compact calendar-date field, to use directly in a `TypedDict`'s annotations.

Bitget's broker-commission endpoints (`classic.broker.agent_customer_commissions`'s
`date`, `classic.broker.agent_customer_trade_volume`'s `time`) send a bare `YYYYMMDD`
date with no separators (e.g. `"20260101"`), not RFC 3339's `YYYY-MM-DD` -- confirmed
against both endpoints' own upstream doc examples.
"""
