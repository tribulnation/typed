"""Etherscan's one wire timestamp shape, plus small domain conversions shared across
the transaction-shaped endpoints."""

from typing_extensions import Annotated, TypedDict
from datetime import datetime, timezone
from decimal import Decimal
from pydantic import BeforeValidator

from typed_core.times import EpochConverter

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
TimestampSeconds = Annotated[datetime, BeforeValidator(timestamp_seconds.parse)]
"""A Unix epoch in seconds, as Etherscan's request-side `timestamp` parameters carry it."""


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
