"""Etherscan's one wire timestamp shape, plus small domain conversions shared across
the transaction-shaped endpoints."""

from typing_extensions import Annotated, TypedDict
from datetime import date, datetime, timezone
from decimal import Decimal
from pydantic import BeforeValidator, PlainSerializer

from typed_core.times import DateConverter, EpochConverter

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
TimestampSeconds = Annotated[
  datetime,
  BeforeValidator(timestamp_seconds.parse),
  PlainSerializer(timestamp_seconds.dump, when_used='json'),
]
"""A Unix epoch in seconds, as Etherscan's request-side `timestamp` parameters carry it.

`PlainSerializer` (ADR 0020/S27) is load-bearing here, not just symmetry: the codegen
mechanization migration serializes every request through `validator(Request).dump(...)`
(design §7), including `blocks.number_by_time`'s `timestamp` field, so a missing
serializer would silently render it as an ISO-8601 string instead of the epoch-seconds
integer Etherscan's wire actually expects -- exactly the live bug ADR 0020 itself warns
was "latent... harmless only until one of them dumps a body through pydantic"."""

date_iso = DateConverter()
DateIso = Annotated[
  date,
  BeforeValidator(date_iso.parse),
  PlainSerializer(date_iso.dump, when_used='json'),
]
"""A plain calendar date field with no time component (`chainTimeStamp`, `UTCDate`, ...),
to use directly in a generated `TypedDict`'s annotations."""


class Value(TypedDict):
  value: str
  """Ether value, in wei."""


def wei2eth(wei: Decimal | int) -> Decimal:
  """Convert a wei amount to ETH."""
  return wei / Decimal(10**18)


def tx_value(tx: Value) -> Decimal:
  """Transaction value, in ETH."""
  return wei2eth(Decimal(tx['value']))


class GasFields(TypedDict):
  gas: str
  """Gas limit, in gas."""
  gasPrice: str
  """Gas price, in wei per gas."""
  gasUsed: str
  """Gas used, in gas."""
  cumulativeGasUsed: str
  """Cumulative gas used in the block up to and including this transaction, in gas."""


def tx_fee(tx: GasFields) -> Decimal:
  """Transaction fee, in ETH."""
  used = Decimal(tx['gasUsed'])
  price = Decimal(tx['gasPrice'])
  return wei2eth(price * used)
