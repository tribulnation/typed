"""Turning an endpoint's `Request` value into wire-ready values: the path, the query
string and the JSON body bytes. Every transport sends exactly what these return."""

from typing_extensions import Any, Mapping
from decimal import Decimal
from types import UnionType
from urllib.parse import quote, urlencode
import json

from pydantic_core import PydanticSerializationError

from typed_core.decimals import plain
from typed_core.validation import validator

from ..exc import LogicError


def dump_request(request: Any, request_type: type | UnionType | None) -> dict[str, Any]:
  """Serialize a `Request` through its own validator, applying every declared format's
  serializer (`datetime` to epoch milliseconds, `Decimal` to a plain-notation string),
  into a plain dict; `{}` for a parameterless call.

  A `Decimal` passed where the type also accepts `str` is dumped in plain notation too
  (`0.0000001`, never `1E-7`): the Trading API's decimal pattern refuses exponents.

  Raises:
    LogicError: A value cannot be serialized as its declared type (a `str` where a
      `Decimal` or `datetime` is declared, say). Nothing is sent.
  """
  if request is None:
    return {}
  if request_type is None:
    return dict(request)
  try:
    # `validator` is typed for a class, but a union of request shapes validates the same way.
    dumped = json.loads(validator(request_type).dump(request))  # type: ignore[arg-type]
  except PydanticSerializationError as error:
    raise LogicError(f'Cannot serialize the request: {error}') from error
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


def path_value(value: Any) -> str:
  """One path segment value: lists comma-joined (`pairs,groups`), everything else as a
  string, percent-encoded so a `/` stays inside its segment (`BTC%2FUSD`)."""
  if isinstance(value, list | tuple):
    value = ','.join(str(item) for item in value)
  return quote(str(value), safe=',')


def fill_path(path: str, values: dict[str, Any]) -> str:
  """Substitute every `{name}` placeholder in `path`, removing each used value from
  `values`; what remains is the query string or the body.

  Raises:
    LogicError: A placeholder has no value.
  """
  while (start := path.find('{')) != -1:
    end = path.index('}', start)
    name = path[start + 1 : end]
    if values.get(name) is None:
      raise LogicError(f'Missing path parameter {name!r} for {path!r}')
    path = path[:start] + path_value(values.pop(name)) + path[end + 1 :]
  return path


def query_value(value: Any) -> str:
  """One query value: booleans as `true`/`false`, everything else as a string."""
  if isinstance(value, bool):
    return 'true' if value else 'false'
  return str(value)


def encode_query(values: Mapping[str, Any]) -> str:
  """The query string for `values`, in order: `None` dropped, lists as repeated keys."""
  items: list[tuple[str, str]] = []
  for key, value in values.items():
    if value is None:
      continue
    if isinstance(value, list | tuple):
      items.extend((key, query_value(item)) for item in value if item is not None)
    else:
      items.append((key, query_value(value)))
  return urlencode(items)


def json_body(values: Mapping[str, Any]) -> bytes:
  """The JSON body bytes for `values`: compact, keys sorted, UTF-8.

  The Trading API hashes the body bytes it receives and never re-serializes them, so any
  stable form verifies as long as these exact bytes are what is signed and sent. Sorted
  and compact is also the canonical (RFC 8785) form, so the body verifies even against a
  server that canonicalized it first.
  """
  return json.dumps(
    values, separators=(',', ':'), sort_keys=True, ensure_ascii=False
  ).encode()
