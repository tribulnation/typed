"""Serializing a generated `Request` value into wire-ready values."""

from typing_extensions import Any, cast
from types import UnionType
import json

from typed_core.validation import validator


def dump_request(
  request: Any, request_type: type | UnionType | None
) -> dict[str, Any] | None:
  """Serialize a generated `Request` value through its own validator into a plain dict,
  with every declared format's serializer applied (a `datetime` becomes its epoch
  number), or `None` for a parameterless call. Key order is the order the value was
  built in, which is the order parameters are sent and signed in.
  """
  if request_type is None or request is None:
    return None
  return json.loads(validator(cast(type, request_type)).dump(request))
