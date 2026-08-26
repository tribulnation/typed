from functools import lru_cache
from typing_extensions import TypeVar, Generic, TypedDict as _TypedDict, Any
import pydantic
from .exceptions import ValidationError

T = TypeVar('T')

@pydantic.with_config(pydantic.ConfigDict(extra='allow'))
class TypedDict(_TypedDict):
  """Base for every generated wire-shape `TypedDict`; tolerates undocumented fields."""


@lru_cache(maxsize=None)
def _adapter(Type: type) -> pydantic.TypeAdapter:
  """Build a `TypeAdapter` for `Type`, cached so every `validator(Type)` call site after the first reuses it."""
  return pydantic.TypeAdapter(Type)


class validator(Generic[T]):
  """Pydantic-backed validator that raises `typed_core.ValidationError` on mismatch.

  `TypeAdapter` construction is the expensive part of validating a response, so it's
  cached per `Type` rather than rebuilt on every generated `validator(Type)` call site:
  the first call against a given `Type` pays for it, every call after (including from
  other endpoints sharing the same response type) reuses the cached adapter.
  """

  def __init__(self, Type: type[T]):
    self.adapter = _adapter(Type)

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