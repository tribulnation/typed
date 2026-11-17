"""Turning an endpoint's `Request` value into wire-ready values."""

from typing_extensions import Any, Literal, Mapping
from decimal import Decimal
from types import UnionType
import json

from typed_core.decimals import plain
from typed_core.validation import validator

SubaccountField = Literal['subaccount', 'sender']
"""The request field naming a call's subaccount (`bytes32` hex), which the core can default
to the client's own (`meta.default_subaccount`)."""


def dump_request(request: Any, request_type: type | UnionType | None) -> dict[str, Any]:
  """Serialize a `Request` through its own validator, applying every declared format's
  serializer (`datetime` to its epoch unit, ...), into a plain dict; `{}` for a
  parameterless call.

  Every `Decimal` the caller passed is sent in plain notation (`10`, `0.00000005`), never
  the scientific form pydantic's dump produces for some values (`1E+1`).
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
