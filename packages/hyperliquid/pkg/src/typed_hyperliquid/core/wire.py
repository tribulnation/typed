"""Shared wire-serialization helper for `info`/`exchange`'s `.request()` (design §2/§7):
dumping a generated `Request` value through its own validator, once, the way every
resolved core needs it before rearranging the result into that surface's real wire shape.
"""

from typing_extensions import Any, cast
from types import UnionType
import json

from typed_core.validation import validator


def dump_request(request: Any, request_type: type | UnionType | None) -> dict[str, Any]:
  """Serialize a generated `request` value through its own validator (ADR 0020/S28),
  returning a plain wire-ready dict with every declared `format` already applied.

  Args:
    request: The generated `Request` value (a `TypedDict` instance), or `None` for a
      parameterless operation.
    request_type: The generated request type, used to build the validator. `None` when
      the endpoint declares no `request` schema at all.

  Returns:
    An empty dict when there's no request schema or value to dump.
  """
  if request_type is None or request is None:
    return {}
  return json.loads(validator(cast(type, request_type)).dump(request))
