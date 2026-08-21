"""Shared Moralis public types, including the wire-timestamp pairs Moralis's spec
declares (`docs/spec/authoring.md` rule 3): `epoch-seconds`, `epoch-millis`, `date-time`,
and `date`.
"""

from datetime import date, datetime, timezone
from typing_extensions import Annotated, Literal

from pydantic import BeforeValidator
from typed_core.times import DateConverter, EpochConverter, IsoConverter


timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
TimestampSeconds = Annotated[datetime, BeforeValidator(timestamp_seconds.parse)]
"""A Moralis Unix-epoch-seconds timestamp field."""

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
TimestampMillis = Annotated[datetime, BeforeValidator(timestamp_millis.parse)]
"""A Moralis Unix-epoch-milliseconds timestamp field."""

timestamp_iso = IsoConverter()
TimestampIso = Annotated[datetime, BeforeValidator(timestamp_iso.parse)]
"""A Moralis RFC 3339 timestamp field."""

date_iso = DateConverter()
DateIso = Annotated[date, BeforeValidator(date_iso.parse)]
"""A Moralis plain-calendar-date field, with no time component."""


Chain = Literal[
  'eth',
  '0x1',
  'sepolia',
  '0xaa36a7',
  'polygon',
  '0x89',
  'bsc',
  '0x38',
  'arbitrum',
  '0xa4b1',
  'base',
  '0x2105',
  'optimism',
  '0xa',
  'avalanche',
  '0xa86a',
  'fantom',
  '0xfa',
  'cronos',
  '0x19',
  'gnosis',
  '0x64',
  'linea',
  '0xe708',
  'moonbeam',
  '0x504',
  'moonriver',
  '0x505',
  'ronin',
  '0x7e4',
  'lisk',
  '0x46f',
  'sei',
  '0x531',
]
"""Moralis EVM chain identifier accepted by wallet endpoints."""

Order = Literal['ASC', 'DESC']
"""Pagination sort order."""

Direction = Literal['receive', 'send']
"""Moralis transfer direction for wallet-relative transfer entries."""
