"""Turning an endpoint's `Request` value into wire-ready values."""

from typing_extensions import Any, Mapping
from types import UnionType
import json

from typed_core.validation import validator


def dump_request(request: Any, request_type: type | UnionType | None) -> dict[str, Any]:
  """Serialize a `Request` through its own validator, applying every declared format's
  serializer, into a plain dict; `{}` for a parameterless call."""
  if request is None:
    return {}
  if request_type is None:
    return dict(request)
  # `validator` is typed for a class, but a union of request shapes validates the same way.
  return json.loads(validator(request_type).dump(request))  # type: ignore[arg-type]


def query_values(values: Mapping[str, Any]) -> dict[str, str]:
  """Flatten values for a query string: booleans as `true`/`false`, lists comma-joined
  (`market_ids=4095,4096`; a JSON array is rejected with `20001 invalid param`)."""
  flat: dict[str, str] = {}
  for key, value in values.items():
    if value is None:
      continue
    if isinstance(value, bool):
      flat[key] = 'true' if value else 'false'
    elif isinstance(value, list):
      flat[key] = ','.join(str(item) for item in value)
    else:
      flat[key] = str(value)
  return flat


def form_values(values: Mapping[str, Any]) -> dict[str, str]:
  """Flatten values for a form body: booleans as `true`/`false`, lists and objects
  JSON-encoded (the form endpoints' convention: `api_key_indexes="[4,5]"`, `tx_types`,
  `tx_infos`)."""
  flat: dict[str, str] = {}
  for key, value in values.items():
    if value is None:
      continue
    if isinstance(value, bool):
      flat[key] = 'true' if value else 'false'
    elif isinstance(value, list | dict):
      flat[key] = json.dumps(value, separators=(',', ':'))
    else:
      flat[key] = str(value)
  return flat


def fill_path(path: str, values: dict[str, Any]) -> str:
  """Substitute `{name}` placeholders in `path`, removing each used value from `values`."""
  while (start := path.find('{')) != -1:
    end = path.index('}', start)
    name = path[start + 1 : end]
    path = path[:start] + str(values.pop(name)) + path[end + 1 :]
  return path
