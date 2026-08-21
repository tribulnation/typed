"""Helpers for Cosmos protobuf Any type URLs."""

import betterproto2
from typing_extensions import TypeVar

from typed_dydx.protos.google.protobuf import Any

BETTERPROTO_TYPE_PREFIX = 'type.googleapis.com/'
COSMOS_TYPE_PREFIX = '/'

T = TypeVar('T', bound=betterproto2.Message)

def type_name(type_url: str) -> str:
  """Return the protobuf type name from an Any type URL."""
  type_url = type_url.removeprefix(BETTERPROTO_TYPE_PREFIX)
  return type_url.removeprefix(COSMOS_TYPE_PREFIX)

def pack_cosmos_any(message: betterproto2.Message) -> Any:
  """Pack a message using Cosmos slash-prefixed type URLs."""
  packed = Any.pack(message)
  return Any(
    type_url=f'{COSMOS_TYPE_PREFIX}{type_name(packed.type_url)}',
    value=packed.value,
  )

def unpack_any(any_message: Any) -> betterproto2.Message | None:
  """Unpack an Any payload across supported type URL forms."""
  try:
    return any_message.unpack()
  except TypeError:
    normalized = Any(
      type_url=f'{BETTERPROTO_TYPE_PREFIX}{type_name(any_message.type_url)}',
      value=any_message.value,
    )
    return normalized.unpack()

def unpack_expected(any_message: Any, expected_type: type[T]) -> T:
  """Unpack an Any payload and require a specific message type."""
  message = unpack_any(any_message)
  if not isinstance(message, expected_type):
    raise TypeError(f'Expected {expected_type.__name__}, got {type(message).__name__}')
  return message
