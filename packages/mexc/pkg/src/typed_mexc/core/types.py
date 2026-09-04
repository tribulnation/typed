"""MEXC's wire timestamp shapes and a handful of shared closed-set types.

`PlainSerializer` pairs with every `BeforeValidator` below (ADR 0020/S27) -- not just
decorative symmetry: the universal `Generator`'s `request()` (design §7/S28) now
serializes every generated request through `validator(Request).dump(request)`, and
without a matching `PlainSerializer`, `dump()` would silently render a
`TimestampMillis`/`TimestampSeconds` field as an ISO-8601 string on the wire regardless
of MEXC's real epoch format -- exactly the class of bug S27 exists to close, now
load-bearing rather than latent the moment a signed request carries a declared
timestamp parameter (e.g. `futures.market.funding_rate_history`'s `start`/`end`).
"""

from typing_extensions import Annotated, Literal
from datetime import datetime, timezone
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import EpochConverter

OrderSide = Literal['BUY', 'SELL']
OrderType = Literal['LIMIT', 'MARKET', 'LIMIT_MAKER', 'IMMEDIATE_OR_CANCEL', 'FILL_OR_KILL', 'STOP_LIMIT_ORDER']
OrderStatus = Literal['NEW', 'FILLED', 'PARTIALLY_FILLED', 'CANCELED', 'PARTIALLY_CANCELED']
TimeInForce = Literal['GTC', 'IOC', 'FOK']

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
"""MEXC's common wire timestamp shape: millisecond epoch, UTC."""

TimestampMillis = Annotated[
  datetime,
  BeforeValidator(timestamp_millis.parse),
  PlainSerializer(timestamp_millis.dump, when_used='json'),
]
"""A millisecond-epoch timestamp field, to use directly in a generated `TypedDict`'s
annotations. Most MEXC timestamp fields are this shape."""

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
"""MEXC's second-epoch wire timestamp shape, UTC -- a minority of fields (documented
in seconds rather than milliseconds), e.g. futures candle windows."""

TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""A second-epoch timestamp field. See `TimestampMillis` for the (far more common)
millisecond-epoch shape."""
