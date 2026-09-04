"""Spot's response envelope and its mapping onto `typed_core` exceptions.

Spot returns bare JSON on success -- the payload itself, no wrapper -- and
`{"code": <int>, "msg": <str>}` with a non-zero `code` on failure. Two discriminators
decide failure: the embedded `code`, and the HTTP status itself (MEXC also signals
malformed requests, auth failures and rate limits via status alone).
"""

from typing_extensions import Any
import json

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited
from typed_core.validation import TypedDict, validator


class ErrorEnvelope(TypedDict):
  """Spot's error shape. A successful response has no wrapper at all."""

  code: int
  msg: str


validate_error = validator(ErrorEnvelope)

AUTH_CODES = frozenset({401, 403, 602, 700001, 700002, 700003, 700004, 700005})
"""Codes MEXC's spot error-code table marks as key/signature/permission rejections."""


def is_error(payload: Any) -> bool:
  """Whether a successfully-decoded JSON body is spot's `{code, msg}` error shape."""
  return isinstance(payload, dict) and 'code' in payload and 'msg' in payload and payload['code'] != 0


def raise_code(code: int, msg: str, payload: Any):
  """Raise the `typed_core` exception matching a non-zero embedded `code`.

  Args:
    code: Spot's own error code.
    msg: Spot's own error message.
    payload: The full error envelope, attached to the exception for debugging.

  Raises:
    AuthError: Key, signature or permission rejection.
    ApiError: Any other non-zero code.
  """
  if code in AUTH_CODES:
    raise AuthError(code, msg, payload)
  raise ApiError(code, msg, payload)


def raise_http_status(response):
  """Raise the `typed_core` exception matching a non-2xx HTTP status.

  Args:
    response: The unsuccessful HTTP response.

  Raises:
    AuthError: Status `401` or `403`.
    RateLimited: Status `429`.
    BadRequest: Any other `4xx` status.
    ApiError: Any other unsuccessful status.
  """
  try:
    payload: Any = response.json()
  except ValueError:
    payload = response.text
  status = response.status_code
  if status in (401, 403):
    raise AuthError(status, payload)
  if status == 429:
    raise RateLimited(status, payload)
  if 400 <= status < 500:
    raise BadRequest(status, payload)
  raise ApiError(status, payload)


def unwrap(response) -> Any:
  """Return the response body, raising on either failure discriminator.

  Args:
    response: The HTTP response to unwrap.

  Raises:
    ValidationError: The body was not JSON.
    ApiError: The embedded `code` was non-zero, or the HTTP status was unsuccessful.
  """
  if not response.is_success:
    raise_http_status(response)
  payload: Any = json.loads(response.text)
  if is_error(payload):
    error = validate_error.python(payload)
    raise_code(error['code'], error['msg'], payload)
  return payload
