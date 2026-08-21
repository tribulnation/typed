"""
Pins `IsoConverter`'s RFC 3339 handling and the missing `EpochConverter.microseconds()`
factory. `IsoConverter` previously round-tripped only `datetime.isoformat()`'s own output
(no `Z`, no over-precision handling) -- venues send `Z`-suffixed timestamps with anywhere
from no fractional digits to nanoseconds (kraken's `post_trade`: `...123456789Z`), and
`datetime.fromisoformat` only understands `Z` and arbitrary fraction lengths from Python
3.11 on, one minor version above this package's declared floor (`>=3.10`).
"""
from datetime import date, datetime, timezone, timedelta
from pydantic import TypeAdapter

from typed_core.times.date import DateConverter
from typed_core.times.iso import IsoConverter
from typed_core.times.ms import EpochConverter


class TestIsoConverterParse:
  def test_z_suffixed_nine_digit_fraction(self):
    """Kraken's `post_trade` example: nanosecond precision, more than `datetime` holds."""
    dt = IsoConverter().parse('2024-05-30T12:34:56.123456789Z')
    assert dt == datetime(2024, 5, 30, 12, 34, 56, 123456, tzinfo=timezone.utc)

  def test_z_suffixed_two_digit_fraction(self):
    """Under-precision, not just over: pre-3.11 `fromisoformat` accepts only exactly 3 or
    6 fractional digits, so a 2-digit wire value has to be padded, not just truncated."""
    dt = IsoConverter().parse('2024-05-30T12:34:56.12Z')
    assert dt == datetime(2024, 5, 30, 12, 34, 56, 120000, tzinfo=timezone.utc)

  def test_z_suffixed_no_fraction(self):
    dt = IsoConverter().parse('2024-05-30T12:34:56Z')
    assert dt == datetime(2024, 5, 30, 12, 34, 56, tzinfo=timezone.utc)

  def test_explicit_offset_is_preserved(self):
    """A non-UTC offset isn't `Z`-normalized on parse -- nothing is lost."""
    dt = IsoConverter().parse('2024-05-30T14:34:56+02:00')
    assert dt == datetime(2024, 5, 30, 12, 34, 56, tzinfo=timezone.utc)


class TestIsoConverterDump:
  def test_naive_datetime_treated_as_already_utc(self):
    """Not converted through the process's local timezone -- attached, not shifted."""
    assert IsoConverter().dump(datetime(2024, 5, 30, 12, 34, 56)) == '2024-05-30T12:34:56Z'

  def test_aware_non_utc_datetime_is_converted(self):
    aware = datetime(2024, 5, 30, 14, 34, 56, tzinfo=timezone(timedelta(hours=2)))
    assert IsoConverter().dump(aware) == '2024-05-30T12:34:56Z'

  def test_bit2me_shape_round_trips(self):
    """Confirmed-working shape from the bit2me handoff: `isoformat().replace('+00:00', 'Z')`."""
    conv = IsoConverter()
    assert conv.dump(conv.parse('2024-05-07T14:08:30.961Z')) == '2024-05-07T14:08:30.961000Z'


class TestIsoConverterPydantic:
  def test_validates_through_annotated_type(self):
    from typing_extensions import Annotated
    from pydantic import BeforeValidator
    converter = IsoConverter()
    TimestampIso = Annotated[datetime, BeforeValidator(converter.parse)]
    validated = TypeAdapter(TimestampIso).validate_python('2024-05-30T12:34:56.123456789Z')
    assert validated == datetime(2024, 5, 30, 12, 34, 56, 123456, tzinfo=timezone.utc)


class TestEpochConverterMicroseconds:
  def test_factory_exists_and_round_trips(self):
    """`epoch-micros` is declared in `EPOCH_FORMATS` (Task 2) but had no factory."""
    conv = EpochConverter.microseconds(tz=timezone.utc)
    dt = datetime(2024, 5, 30, 12, 34, 56, 123456, tzinfo=timezone.utc)
    assert conv.dump(dt) == int(dt.timestamp() * 1_000_000)
    assert conv.parse(conv.dump(dt)) == dt


class TestEpochConverterNanoseconds:
  def test_factory_exists_and_round_trips(self):
    """`epoch-nanos` (deribit's `starbase_timestamp`/`starbase_last_update_timestamp`) had
    no factory -- `EpochConverter` was already generic on `unit`, just missing this one."""
    conv = EpochConverter.nanoseconds(tz=timezone.utc)
    dt = datetime(2024, 5, 30, 12, 34, 56, 123456, tzinfo=timezone.utc)
    assert conv.dump(dt) == int(dt.timestamp() * 1_000_000_000)
    assert conv.parse(conv.dump(dt)) == dt


class TestDateConverter:
  def test_parse(self):
    """Plain calendar date, no time component -- deribit's
    `market_data.get_delivery_prices.date` (e.g. `'2026-08-03'`)."""
    assert DateConverter().parse('2026-08-03') == date(2026, 8, 3)

  def test_dump(self):
    assert DateConverter().dump(date(2026, 8, 3)) == '2026-08-03'

  def test_round_trips(self):
    conv = DateConverter()
    assert conv.parse(conv.dump(date(2026, 8, 3))) == date(2026, 8, 3)


class TestDateConverterPydantic:
  def test_validates_through_annotated_type(self):
    from typing_extensions import Annotated
    from pydantic import BeforeValidator
    converter = DateConverter()
    DateIso = Annotated[date, BeforeValidator(converter.parse)]
    validated = TypeAdapter(DateIso).validate_python('2026-08-03')
    assert validated == date(2026, 8, 3)
