from typing_extensions import Annotated, Literal
from datetime import datetime, timezone
from pydantic import BeforeValidator

from typed_core.times import EpochConverter

OrderSide = Literal['BUY', 'SELL']
OrderType = Literal['LIMIT', 'MARKET', 'LIMIT_MAKER', 'IMMEDIATE_OR_CANCEL', 'FILL_OR_KILL', 'STOP_LIMIT_ORDER']
OrderStatus = Literal['NEW', 'FILLED', 'PARTIALLY_FILLED', 'CANCELED', 'PARTIALLY_CANCELED']
TimeInForce = Literal['GTC', 'IOC', 'FOK']

timestamp = EpochConverter.milliseconds(tz=timezone.utc)
"""MEXC's common wire timestamp shape: millisecond epoch, UTC."""

Timestamp = Annotated[datetime, BeforeValidator(timestamp.parse)]
"""A millisecond-epoch timestamp field, to use directly in a generated `TypedDict`'s
annotations. Most MEXC timestamp fields are this shape."""

timestamp_s = EpochConverter.seconds(tz=timezone.utc)
"""MEXC's second-epoch wire timestamp shape, UTC -- a minority of fields (documented
in seconds rather than milliseconds), e.g. futures candle windows."""

TimestampSeconds = Annotated[datetime, BeforeValidator(timestamp_s.parse)]
"""A second-epoch timestamp field. See `Timestamp` for the (far more common)
millisecond-epoch shape."""
