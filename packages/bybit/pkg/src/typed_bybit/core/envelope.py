"""The Bybit v5 response envelope and its mapping onto `typed_core` exceptions.

Every v5 REST response is wrapped in `{retCode, retMsg, result, retExtInfo, time}`.
`retCode == 0` means success; anything else is an API error even though the HTTP
status is still `200`. Generated endpoints therefore type only the `result` payload
and let the core unwrap and raise.

References:
  - [Bybit error codes](https://bybit-exchange.github.io/docs/v5/error)
"""

from typing_extensions import Any, NotRequired
import httpx

from typed_core.exceptions import (
  ApiError,
  AuthError,
  BadRequest,
  RateLimited,
  ValidationError,
)

from .validation import TypedDict


class Envelope(TypedDict):
  """Common wrapper around every Bybit v5 REST response."""

  retCode: int
  """Return code; `0` means success."""
  retMsg: str
  """Return message; `OK`, `SUCCESS` or an error description."""
  result: NotRequired[Any]
  """Endpoint-specific payload."""
  retExtInfo: NotRequired[Any]
  """Extended error information, usually an empty object."""
  time: NotRequired[int]
  """Server timestamp in milliseconds."""


AUTH_RET_CODES = frozenset({10003, 10004, 10005, 10010, 10016, 33004})
"""`retCode` values that mean the key, signature, permissions or IP were rejected."""

RATE_LIMIT_RET_CODES = frozenset({10006, 10018, 10429, 20003})
"""`retCode` values that mean the request was throttled."""

BAD_REQUEST_RET_CODES = frozenset({10001, 10002, 10009, 20006})
"""`retCode` values that mean the request itself was malformed."""


def raise_ret_code(ret_code: int, ret_msg: str, payload: Any):
  """Raise the `typed_core` exception matching a non-zero `retCode`.

  Args:
    ret_code: The `retCode` returned by Bybit.
    ret_msg: The `retMsg` returned by Bybit.
    payload: The full envelope, attached to the exception for debugging.

  Raises:
    AuthError: Credential, signature, permission or IP rejection.
    RateLimited: Request throttled by Bybit.
    BadRequest: Malformed request parameters.
    ApiError: Any other non-zero `retCode`.
  """
  if ret_code in AUTH_RET_CODES:
    raise AuthError(ret_code, ret_msg, payload)
  if ret_code in RATE_LIMIT_RET_CODES:
    raise RateLimited(ret_code, ret_msg, payload)
  if ret_code in BAD_REQUEST_RET_CODES:
    raise BadRequest(ret_code, ret_msg, payload)
  raise ApiError(ret_code, ret_msg, payload)


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
  """Return the `result` payload of a Bybit v5 response.

  Args:
    response: The HTTP response to unwrap.

  Raises:
    ValidationError: The body was not a JSON v5 envelope.
    ApiError: `retCode` was non-zero, or the HTTP status was unsuccessful.
  """
  if not response.is_success:
    raise_http_status(response)
  try:
    envelope: Any = response.json()
  except ValueError as e:
    raise ValidationError('Bybit response was not valid JSON', response.text) from e
  if not isinstance(envelope, dict) or 'retCode' not in envelope:
    raise ValidationError('Bybit response is not a v5 envelope', envelope)
  ret_code = envelope['retCode']
  if ret_code != 0:
    raise_ret_code(ret_code, envelope.get('retMsg', ''), envelope)
  return envelope.get('result')
