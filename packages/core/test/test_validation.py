"""`validator` surfaces pydantic's own report as the `ValidationError` message: a pydantic
v2 error has empty `args`, so `ValidationError(*e.args)` read as a bare `ValidationError()`
and every SDK boundary translating client errors forwarded an empty message."""
from typing_extensions import TypedDict
import pytest

from typed_core.exceptions import ValidationError
from typed_core.validation import validator


class Row(TypedDict):
  price: int


def test_message_names_the_field_and_the_offending_value():
  with pytest.raises(ValidationError) as info:
    validator(Row).python({'price': 'abc'})
  message = str(info.value)
  assert 'price' in message and 'abc' in message


def test_json_path_carries_the_same_report():
  with pytest.raises(ValidationError) as info:
    validator(Row).json(b'{"price": null}')
  assert 'price' in str(info.value)


def test_pydantic_error_stays_on_cause():
  import pydantic
  with pytest.raises(ValidationError) as info:
    validator(Row).python({})
  assert isinstance(info.value.__cause__, pydantic.ValidationError)
  assert info.value.__cause__.errors()[0]['loc'] == ('price',)
