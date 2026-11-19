"""JSON encoding and decoding, and the mapping of HTTP errors onto `typed_core` exceptions.

EVEDEX sends prices and quantities as JSON numbers, so responses are decoded with
`parse_float=Decimal`: a float would already have lost the venue's precision before
validation sees it. Requests send every `Decimal` as a plain-notation string, which every
numeric request field accepts (`string | number`).
"""

from typing_extensions import Any
from decimal import Decimal
import json

import httpx

from typed_core.decimals import plain

from .exc import ApiError, AuthError, BadRequest, RateLimited, ValidationError


def loads(data: str | bytes) -> Any:
  """Decode a JSON document, keeping every non-integer number a `Decimal`.

  Raises:
    ValidationError: `data` is not JSON.
  """
  try:
    return json.loads(data, parse_float=Decimal)
  except ValueError as e:
    raise ValidationError(f'Invalid JSON: {data[:200]!r}') from e


def encode(value: Any) -> Any:
  """`json.dumps`'s `default`: a `Decimal` becomes a plain-notation string.

  Raises:
    TypeError: `value` is not JSON-serializable.
  """
  if isinstance(value, Decimal):
    return plain(value)
  raise TypeError(f'Object of type {type(value).__name__} is not JSON serializable')


def dumps(value: Any) -> str:
  """Encode a request body compactly, `Decimal`s as plain strings."""
  return json.dumps(value, default=encode, separators=(',', ':'))


AUTH_LABELS = frozenset({'user_not_found_error', 'invalid_signature_error'})
"""Labels that mean the credential, not the request, is at fault, whatever the status:
`user_not_found_error` (`404`) is a wallet signed in on the Auth service with no exchange
account yet (`POST /api/user/account` creates it), and `invalid_signature_error` (`400`)
an EIP-712 signature the venue rejected."""


def raise_for_status(response: httpx.Response):
  """Raise the `typed_core` exception matching an unsuccessful response.

  An error body is `{tagId, date, error, label}`; `label` names the failure
  (`unauthorized_error`, `instrument_not_found_error`) but is not reliable on its own: a
  query that fails validation answers `400` labelled `internal_server_error`. So the HTTP
  status decides the exception, and the body rides along on it.

  Raises:
    AuthError: Status `401` or `403`, or a label in `AUTH_LABELS`.
    RateLimited: Status `429`.
    BadRequest: Any other `4xx` status.
    ApiError: Any other unsuccessful status.
  """
  if response.is_success:
    return
  try:
    payload: Any = loads(response.text)
  except ValidationError:
    payload = response.text
  status = response.status_code
  if status in (401, 403):
    raise AuthError(status, payload)
  if isinstance(payload, dict) and payload.get('label') in AUTH_LABELS:
    raise AuthError(status, payload)
  if status == 429:
    raise RateLimited(status, payload)
  if 400 <= status < 500:
    raise BadRequest(status, payload)
  raise ApiError(status, payload)


def unwrap(response: httpx.Response) -> Any:
  """Return the bare JSON payload of a successful response, raising on failure.

  An empty `2xx` body (some writes answer with none) decodes to `None`.
  """
  raise_for_status(response)
  if not response.content:
    return None
  return loads(response.text)
