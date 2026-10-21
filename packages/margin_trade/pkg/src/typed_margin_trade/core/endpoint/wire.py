"""Turning an endpoint's `Request` value into wire-ready values."""

from typing_extensions import Any, Mapping
from types import UnionType
import json

from typed_core.validation import validator


def dump_request(request: Any, request_type: type | UnionType | None) -> dict[str, Any]:
  """Serialize a `Request` through its own validator, applying every declared format's
  serializer (`PlainDecimal`, timestamps), into a plain dict; `{}` for a parameterless call.

  `None` values are dropped: Margin Trade treats a sent zero/null as "missing" at best and
  rejects it at worst (`startTime: 0` reads as `startTime is required`). Dropping them at the
  top level is enough: no request schema admits `null` at any depth, and an omitted nested
  optional field (a `NotRequired` key of `OrderSpec`, `CandleRange`, ...) is absent from the
  dump rather than `None`.
  """
  if request is None:
    return {}
  elif request_type is None:
    values = dict(request)
  else:
    # `validator` is typed for a class, but a union of request shapes validates the same way.
    values = json.loads(validator(request_type).dump(request))  # type: ignore[arg-type]
  return {key: value for key, value in values.items() if value is not None}


def query_values(values: Mapping[str, Any]) -> dict[str, str]:
  """Flatten values for a query string (`/coingecko/*`): booleans as `true`/`false`."""
  flat: dict[str, str] = {}
  for key, value in values.items():
    if isinstance(value, bool):
      flat[key] = 'true' if value else 'false'
    else:
      flat[key] = str(value)
  return flat
