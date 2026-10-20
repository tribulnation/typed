"""Wire helpers shared by every transport: request serialization, templates, validation."""

from collections.abc import Iterator
from decimal import Decimal
from types import UnionType
import json
import re

import pydantic
from pydantic_core import PydanticSerializationError, to_jsonable_python
from typing_extensions import Any, Mapping, TypeVar, cast

from typed_core.decimals import plain
from typed_core.exceptions import BadRequest
from typed_core.validation import validator

T = TypeVar('T')

PLACEHOLDER = re.compile(r'\{(\w+)\}')
"""A `{name}` placeholder in a path or channel template."""
OPTIONAL_GROUP = re.compile(r'\[([^\[\]]*)\]')
"""A `[...]` group, kept only when every placeholder inside it has a value."""
SELECTOR_ADDRESS = re.compile(r'(?<!\w)0x[0-9a-fA-F]{40}(?!\w)')
"""A whole hex EVM address inside a stream selector, in any case: not part of a longer
word, so an instrument name or a longer hash is never touched."""


class PlainNotation(Decimal):
  """A `Decimal` whose `str()` is plain notation (`50000`, `0.0000001`), never scientific.

  Pydantic dumps a `Decimal` field as `str(value)`, which is `5E+4` for `Decimal('5E+4')`
  and `1E-7` for `Decimal('0.0000001')`; the venue expects plain decimal strings.
  """

  def __str__(self) -> str:
    """Plain notation, every significant digit kept."""
    return plain(self)


def plain_decimals(value: Any) -> Any:
  """Copy a request value with every `Decimal` in it, at any depth, as a `PlainNotation`.

  Args:
    value: The request value: `TypedDict`s, lists and scalars.
  """
  if isinstance(value, Decimal):
    return value if isinstance(value, PlainNotation) else PlainNotation(value)
  if isinstance(value, Mapping):
    return {k: plain_decimals(v) for k, v in value.items()}
  if isinstance(value, list):
    return [plain_decimals(v) for v in value]
  if isinstance(value, tuple):
    return tuple(plain_decimals(v) for v in value)
  return value


def stray_fields(given: Any, kept: Any, path: str = '') -> Iterator[tuple[str, Any]]:
  """Fields of `given`, at any depth, that `kept` (the same value, after a serializer or
  validator processed it) no longer has: the ones the type does not declare.

  Args:
    given: The value as it was before.
    kept: The same value after processing.
    path: Location of `given` in the request, for the error message.
  """
  if isinstance(given, Mapping) and isinstance(kept, Mapping):
    for key, value in given.items():
      where = f'{path}.{key}' if path else str(key)
      if key not in kept:
        yield where, value
      else:
        yield from stray_fields(value, kept[key], where)
  elif isinstance(given, (list, tuple)) and isinstance(kept, (list, tuple)):
    for i, (item, kept_item) in enumerate(zip(given, kept)):
      yield from stray_fields(item, kept_item, f'{path}[{i}]')


def numbers_as_strings(given: Any, wire: Any, path: str = '') -> Iterator[str]:
  """Paths, at any depth, where `given` holds a number (an `int`, `float` or `bool`) and
  its wire form is a string.

  Only a decimal field turns a number into a string: `PlainDecimal`'s serializer formats
  whatever it is given, unchecked (`1e-7` as `'0.000000'`, `True` as `'1.000000'`), where a
  `Decimal` field's serializer refuses anything but a `Decimal`. No other request field
  does: a string field refuses a number, and a number field keeps it a number.

  Args:
    given: The value as it was before serialization.
    wire: Its wire form.
    path: Location of `given` in the request, for the error message.
  """
  if isinstance(given, Mapping) and isinstance(wire, Mapping):
    for key, value in given.items():
      if key in wire:
        yield from numbers_as_strings(
          value, wire[key], f'{path}.{key}' if path else str(key)
        )
  elif isinstance(given, (list, tuple)) and isinstance(wire, (list, tuple)):
    for i, (item, wire_item) in enumerate(zip(given, wire)):
      yield from numbers_as_strings(item, wire_item, f'{path}[{i}]')
  elif isinstance(given, (int, float)) and isinstance(wire, str):
    yield path


def stray_message(stray: list[tuple[str, Any]]) -> str:
  """Describe undeclared request fields; a `None` one is a field to leave out instead."""
  nones = [path for path, value in stray if value is None]
  others = [path for path, value in stray if value is not None]
  parts = []
  if others:
    parts.append(f'undeclared field(s) {", ".join(others)}')
  if nones:
    parts.append(f'{", ".join(nones)} set to None (leave it out instead)')
  return '; '.join(parts)


def dump(
  value: Any,
  type_: type[Any] | UnionType | None = None,
  *,
  operation: str | None = None,
) -> Any:
  """Serialize a request value to its JSON-compatible wire form.

  With a declared type, its serializers apply (a `TimestampNanos` becomes a nanosecond
  string), and the value is checked against it: it must serialize as the type (a union as
  one of its variants), the wire form must read back as it, and no field may be one the
  type (or the union variant it reads back as) does not declare, at any depth. A pydantic
  serializer silently drops such a field, and a validator ignores it, so a misspelt
  optional field would otherwise go missing unnoticed, and a `None` given for a field
  the variant lacks (`orders=None` on a bulk cancel) would be sent as `null`. A number
  given for a decimal field (`PlainDecimal | str`) is refused too, since its serializer
  would format it unchecked and rounded (see `numbers_as_strings`). Without a type,
  pydantic's defaults apply, unchecked.

  Either way every `Decimal` is sent in plain notation (`"50000"`, never `"5E+4"`), a `str`
  given for a decimal is sent untouched (the caller's own notation and precision), and
  whatever is signed afterwards is read from these same wire strings.

  Args:
    value: The request value, usually a `TypedDict`.
    type_: The request's declared type.
    operation: What the request is for, named in the error: an RPC path
      (`/full/v1/create_order`), `stream v1.order`, or an edge `POST /path`.

  Raises:
    BadRequest: The value does not match `type_`: no union variant fits it, a field has
      the wrong type (a number for a decimal included), a required field is missing, or a
      field is not declared (or is `None` where it may only be left out). The message
      names `operation` and the offending fields, e.g. `Request for /full/v2/bulk_orders
      does not match its type: orders set to None (leave it out instead)`.
  """
  if value is None:
    return None
  value = plain_decimals(value)
  if type_ is None:
    return to_jsonable_python(value)
  subject = f'Request for {operation}' if operation else 'Request'
  adapter = validator(cast(type, type_)).adapter
  try:
    raw = adapter.dump_json(value, warnings='error')
  except PydanticSerializationError as e:
    raise BadRequest(f'{subject} does not match its type: {e}') from e
  wire = json.loads(raw)
  try:
    read = adapter.validate_python(wire)
  except pydantic.ValidationError as e:
    raise BadRequest(f'{subject} does not match its type: {e}') from e
  numbers = list(numbers_as_strings(value, wire))
  if numbers:
    raise BadRequest(
      f'{subject} does not match its type: {", ".join(numbers)} must be a Decimal or a '
      'str, not a number'
    )
  stray = [*stray_fields(value, wire), *stray_fields(wire, read)]
  if stray:
    raise BadRequest(f'{subject} does not match its type: {stray_message(stray)}')
  return wire


def load(payload: Any, type_: type[T] | UnionType | None, *, validate: bool) -> T:
  """Validate a decoded payload against its declared type.

  Args:
    payload: The decoded, unwrapped payload.
    type_: The declared response type; `None` returns the payload untouched.
    validate: Whether to validate at all.
  """
  if type_ is None or not validate:
    return payload
  return validator(cast(type, type_)).python(payload)


def normalize_channel(channel: str) -> str:
  """Lowercase every whole `0x` address in the selector of a filled `{stream}:{selector}`
  channel, leaving the stream and every other part of the selector as they are.

  GRVT matches address stream selectors case-sensitively against the lowercase form (the
  one login returns as `funding_account_address`) and refuses an EIP-55 checksummed one
  with `1001`. Normalizing the filled channel, rather than the parameter values, also
  covers an address written straight into the channel (`v1.deposit:0xAbC...`).

  Args:
    channel: The filled channel, e.g. `v1.transfer:0xAbC...-123`.
  """
  stream, sep, selector = channel.partition(':')
  if not sep:
    return channel
  return stream + sep + SELECTOR_ADDRESS.sub(lambda m: m.group(0).lower(), selector)


def fill(template: str, values: Mapping[str, Any]) -> tuple[str, dict[str, Any]]:
  """Fill a path or channel template, returning it with the values it did not consume.

  Args:
    template: Template with `{name}` placeholders and optional `[...]` groups.
    values: Wire values (already serialized by `dump`).

  Raises:
    BadRequest: A placeholder outside any optional group has no value.
  """
  used: set[str] = set()

  def value(name: str) -> str:
    """Render one placeholder's value, recording it as consumed."""
    used.add(name)
    v = values[name]
    return str(v).lower() if isinstance(v, bool) else str(v)

  def group(match: re.Match[str]) -> str:
    """Render an optional group, or drop it when any of its placeholders is missing."""
    names = PLACEHOLDER.findall(match.group(1))
    if any(values.get(name) is None for name in names):
      return ''
    return PLACEHOLDER.sub(lambda m: value(m.group(1)), match.group(1))

  filled = OPTIONAL_GROUP.sub(group, template)
  missing = [name for name in PLACEHOLDER.findall(filled) if values.get(name) is None]
  if missing:
    raise BadRequest(f'Missing value for {", ".join(missing)} in {template!r}')
  filled = PLACEHOLDER.sub(lambda m: value(m.group(1)), filled)
  # A placeholder inside a dropped optional group is consumed too: it was never meant to be
  # sent anywhere but the template.
  for match in OPTIONAL_GROUP.finditer(template):
    used.update(PLACEHOLDER.findall(match.group(1)))
  rest = {k: v for k, v in values.items() if k not in used and v is not None}
  return filled, rest
