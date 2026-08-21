"""Bitget-specific wire types: `TimestampMillis`, the venue's epoch-millisecond timestamp
shape, and `DateIso`, its broker-commission endpoints' compact calendar-date shape."""

from typing_extensions import Annotated
from datetime import date, datetime, timezone
from pydantic import BeforeValidator

from typed_core.times import DateConverter, EpochConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)

TimestampMillis = Annotated[datetime, BeforeValidator(timestamp_millis.parse)]
"""A Bitget epoch-millisecond timestamp field, to use directly in a `TypedDict`'s annotations.

Bitget sends epoch-millisecond timestamps as either a JSON number or a numeric string
depending on the endpoint (e.g. `serverTime` is a string, WS `ts` is a number) —
`EpochConverter.parse` coerces both through `int()` before converting, so this is
invisible from the caller's side.
"""

date_compact = DateConverter(pattern='%Y%m%d')

DateIso = Annotated[date, BeforeValidator(date_compact.parse)]
"""A Bitget compact calendar-date field, to use directly in a `TypedDict`'s annotations.

Bitget's broker-commission endpoints (`classic.broker.agent_customer_commissions`'s
`date`, `classic.broker.agent_customer_trade_volume`'s `time`) send a bare `YYYYMMDD`
date with no separators (e.g. `"20260101"`), not RFC 3339's `YYYY-MM-DD` -- confirmed
against both endpoints' own upstream doc examples.
"""
