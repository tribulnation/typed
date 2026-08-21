"""Futures' response envelope and its mapping onto `typed_core` exceptions.

Unlike spot, futures always wraps its response: `{"success": true, "code": 0, "data":
{...}}` on success, `{"success": false, "code": <int>, "message": <str>}` on error. Per
`spec-authoring.md` rule 5, `unwrap` does **not** strip to `data`: MEXC documents futures
pagination totals beside `data`, not inside it, so already-declared `pagination` blocks
read paths like `data.totalPage` -- paths that only exist because the envelope is kept
whole. Endpoint methods validate and return the *entire* frame.
"""

from typing_extensions import Any
import httpx

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited
from typed_core.validation import TypedDict, validator


class Envelope(TypedDict, total=False):
  """Every futures response. `success: false` (or a non-zero `code`, when present even
  alongside `success: true`) means the request failed.
  """

  success: bool
  code: int
  message: str
  data: Any


validate_envelope = validator(Envelope)

AUTH_CODES = frozenset({401, 402, 406, 701, 702, 703, 704})
"""Codes MEXC's futures error-code table marks as auth/permission rejections."""

RATE_LIMIT_CODES = frozenset({510, 511, 513})
"""Codes that mean the request was throttled or the request time drifted."""


def raise_code(code: int, message: str, payload: Any):
  """Raise the `typed_core` exception matching a non-zero embedded `code`.

  Args:
    code: Futures' own error code.
    message: Futures' own error message.
    payload: The full envelope, attached to the exception for debugging.

  Raises:
    AuthError: Auth or permission rejection.
    RateLimited: Request throttled, or request time outside the accepted window.
    ApiError: Any other non-zero code.
  """
  if code in AUTH_CODES:
    raise AuthError(code, message, payload)
  if code in RATE_LIMIT_CODES:
    raise RateLimited(code, message, payload)
  raise ApiError(code, message, payload)


def raise_http_status(response: httpx.Response):
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


def unwrap(response: httpx.Response) -> Any:
  """Return the whole envelope, raising on either failure discriminator.

  Args:
    response: The HTTP response to unwrap.

  Raises:
    ValidationError: The body was not JSON, or not a recognizable envelope.
    ApiError: `success` was false, the embedded `code` was non-zero, or the HTTP status
      was unsuccessful.
  """
  if not response.is_success:
    raise_http_status(response)
  envelope = validate_envelope.json(response.text)
  code = envelope.get('code')
  if envelope.get('success') is False or (code is not None and code != 0):
    raise_code(code or 0, envelope.get('message', ''), envelope)
  return envelope
