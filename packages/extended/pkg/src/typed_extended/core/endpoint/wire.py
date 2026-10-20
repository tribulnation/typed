"""Turning an endpoint's `Request` value into wire-ready values."""

from typing_extensions import Any, Mapping
from decimal import Decimal
from types import UnionType
from urllib.parse import quote
import json

from typed_core.decimals import plain
from typed_core.validation import validator


def dump_request(request: Any, request_type: type | UnionType | None) -> dict[str, Any]:
  """Serialize a `Request` through its own validator, applying every declared format's
  serializer (`Decimal` to string, `datetime` to epoch milliseconds, ...), into a plain
  dict; `{}` for a parameterless call.

  Every `Decimal` the caller passed is sent in plain notation (`10`, `0.00000005`), never
  the scientific form pydantic's `str()` dump produces for some values (`1E+1`, `5E-8`).
  """
  if request is None:
    return {}
  if request_type is None:
    return dict(request)
  # `validator` is typed for a class, but a union of request shapes validates the same way.
  dumped = json.loads(validator(request_type).dump(request))  # type: ignore[arg-type]
  return plain_decimals(request, dumped)


def plain_decimals(original: Any, dumped: Any) -> Any:
  """Walk `original` and its JSON dump together, replacing the dump of every `Decimal`
  in `original` with its plain-notation string."""
  if isinstance(original, Decimal) and isinstance(dumped, str):
    return plain(original)
  if isinstance(original, Mapping) and isinstance(dumped, dict):
    return {
      key: plain_decimals(original[key], value) if key in original else value
      for key, value in dumped.items()
    }
  if (
    isinstance(original, list | tuple)
    and isinstance(dumped, list)
    and len(original) == len(dumped)
  ):
    return [plain_decimals(item, value) for item, value in zip(original, dumped)]
  return dumped


def fill_path(path: str, values: dict[str, Any]) -> str:
  """Substitute `{name}` placeholders in `path`, removing each used value from `values`.

  A placeholder whose value is absent drops its whole path segment: the stream paths'
  optional `{market}` (`/orderbooks/{market}` -> `/orderbooks` for every market). Each
  value is percent-encoded, so a `/`, `?` or `#` in caller input stays data inside its own
  segment instead of changing the path or starting a query.
  """
  while (start := path.find('{')) != -1:
    end = path.index('}', start)
    name = path[start + 1 : end]
    value = values.pop(name, None)
    if value is None:
      prefix = path[:start]
      prefix = prefix[:-1] if prefix.endswith('/') else prefix
      path = prefix + path[end + 1 :]
    else:
      path = path[:start] + quote(str(value), safe='') + path[end + 1 :]
  return path


def query_values(values: Mapping[str, Any]) -> dict[str, str | list[str]]:
  """Flatten values for a query string: booleans as `true`/`false`, lists as repeated keys
  (`?market=BTC-USD&market=ETH-USD`), `None` dropped."""

  def scalar(value: Any) -> str:
    """One query value as a string."""
    if isinstance(value, bool):
      return 'true' if value else 'false'
    return str(value)

  flat: dict[str, str | list[str]] = {}
  for key, value in values.items():
    if value is None:
      continue
    if isinstance(value, list | tuple):
      flat[key] = [scalar(item) for item in value if item is not None]
    else:
      flat[key] = scalar(value)
  return flat
