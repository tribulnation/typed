"""Venue-specific wire types: KuCoin's timestamp shape threaded through pydantic validation.

References:
  - [KuCoin API docs](https://www.kucoin.com/docs-new)
"""

from typing_extensions import Annotated
from datetime import date, datetime, timezone
from pydantic import BeforeValidator

from typed_core.times import EpochConverter

timestamp_millis = EpochConverter.milliseconds(tz=timezone.utc)
"""Every KuCoin timestamp field is a millisecond Unix epoch integer, UTC — confirmed live
against `/api/v1/timestamp` (Spot and Futures) and `/api/v2/user-info`'s neighboring fields.
"""

TimestampMillis = Annotated[datetime, BeforeValidator(timestamp_millis.parse)]
"""A timestamp field, to use directly in a generated `TypedDict`'s annotations."""

timestamp_seconds = EpochConverter.seconds(tz=timezone.utc)
"""Spot Market's Get Klines (`/api/v1/market/candles`) is a documented exception to
KuCoin's usual millisecond convention: its `startAt`/`endAt` query parameters are a
second Unix epoch integer, UTC.
"""

TimestampSeconds = Annotated[datetime, BeforeValidator(timestamp_seconds.parse)]
"""A second-epoch timestamp field, to use directly in a generated `TypedDict`'s
annotations — Spot Market's Get Klines only; every other KuCoin timestamp is
`TimestampMillis`.
"""

timestamp_nanos = EpochConverter(unit=1e9, tz=timezone.utc)
"""A handful of response-only fields (futures orderbook/ticker/trade `ts`, several stream
push timestamps) are documented in nanoseconds rather than KuCoin's usual milliseconds —
confirmed against each field's own upstream description.
"""

TimestampNanos = Annotated[datetime, BeforeValidator(timestamp_nanos.parse)]
"""A nanosecond-epoch timestamp field, to use directly in a generated `TypedDict`'s
annotations. Response-side only so far — every wire occurrence declaring `epoch-nanos`
is a read-only field; see `docs/spec/authoring.md` rule 3.
"""


class _DateConverter:
  """Converts an RFC 3339 full-date (`YYYY-MM-DD`) to/from a plain `date`.

  `typed_core.times` ships no bare-date primitive — both `EpochConverter` and
  `IsoConverter` parse to a full `datetime` — so this is hand-written rather than reused,
  the same way `HttpRequest.body_value` (`client_generation`) expects any `TIMESTAMP_HELPERS`
  entry to expose a plain `.dump(value)` method, regardless of what built it.
  """

  def parse(self, value: str) -> date:
    """Parse an RFC 3339 full-date string into a `date`."""
    return date.fromisoformat(value)

  def dump(self, value: date) -> str:
    """Render a `date` back to its RFC 3339 full-date wire form."""
    return value.isoformat()


date_iso = _DateConverter()
"""KuCoin's identity-document-adjacent date fields (`broker.kyc_submit`'s `birthDate`/
`expireDate`) are plain `YYYY-MM-DD` calendar dates, no time-of-day component.
"""

DateIso = Annotated[date, BeforeValidator(date_iso.parse)]
"""A calendar-date field (no time-of-day), to use directly in a generated `TypedDict`'s
annotations.
"""
