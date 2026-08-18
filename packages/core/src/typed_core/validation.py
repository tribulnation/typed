from typing_extensions import TypeVar, Generic, TypedDict as _TypedDict, Any
import pydantic
from .exceptions import ValidationError

T = TypeVar('T')

@pydantic.with_config(pydantic.ConfigDict(extra='allow'))
class TypedDict(_TypedDict):
  """Base for every generated wire-shape `TypedDict`; tolerates undocumented fields."""


class validator(Generic[T]):
  """Lazily-built pydantic adapter that raises `typed_core.ValidationError` on mismatch."""

  def __init__(self, Type: type[T]):
    self.adapter = pydantic.TypeAdapter(Type)

  def json(self, data: str | bytes | bytearray) -> T:
    """Validate a raw JSON document."""
    try:
      return self.adapter.validate_json(data)
    except pydantic.ValidationError as e:
      raise ValidationError(*e.args) from e

  def python(self, data: Any) -> T:
    """Validate an already-decoded Python value."""
    try:
      return self.adapter.validate_python(data)
    except pydantic.ValidationError as e:
      raise ValidationError(*e.args) from e

  def __call__(self, data) -> T:
    if isinstance(data, str | bytes | bytearray):
      return self.json(data)
    return self.python(data)