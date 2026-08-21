"""The KuCoin response envelope and its mapping onto `typed_core` exceptions.

Every REST response is wrapped `{code, data, msg}`. `code == "200000"` means success, even
though the HTTP status stays 200 on API errors. `code` is a string, not an int — unlike, say,
bybit's `retCode`.

References:
  - [KuCoin API docs](https://www.kucoin.com/docs-new)
"""

from typing_extensions import Any, NotRequired
import httpx

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited
from typed_core.validation import TypedDict, validator


class Envelope(TypedDict):
  """Every KuCoin REST response."""

  code: str
  """Result code; `"200000"` means success."""
  data: NotRequired[Any]
  """Endpoint-specific payload, present on success."""
  msg: NotRequired[str]
  """Error description, present on failure."""


validate_envelope = validator(Envelope)

AUTH_CODES = frozenset(
  {'400001', '400002', '400003', '400004', '400005', '400006', '400007', '411100'}
)
"""Codes that mean the key, timestamp, signature, passphrase, IP or account itself was
rejected — from KuCoin's own published error descriptions (cross-checked against ccxt's
`kucoin.py` exceptions table, which classifies each of these as an authentication error)."""

RATE_LIMIT_CODES = frozenset({'429000'})
"""Codes that mean the request was throttled."""

BAD_REQUEST_CODES = frozenset({'400100', '400200', '415000'})
"""Codes that mean the request itself was malformed."""


def raise_code(code: str, msg: str, payload: Any):
  """Raise the `typed_core` exception matching a non-success `code`.

  Args:
    code: The venue's own result code.
    msg: The venue's own error message.
    payload: The full envelope, attached to the exception for debugging.

  Raises:
    AuthError: Credential, signature, timestamp or account rejection.
    RateLimited: Request throttled by the venue.
    BadRequest: Malformed request parameters.
    ApiError: Any other non-success code.
  """
  if code in AUTH_CODES:
    raise AuthError(code, msg, payload)
  if code in RATE_LIMIT_CODES:
    raise RateLimited(code, msg, payload)
  if code in BAD_REQUEST_CODES:
    raise BadRequest(code, msg, payload)
  raise ApiError(code, msg, payload)


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
  """Return the `data` payload of a response, raising on either failure discriminator.

  Args:
    response: The HTTP response to unwrap.

  Raises:
    ValidationError: The body was not JSON, or not a recognizable envelope.
    ApiError: `code` was not `"200000"`, or the HTTP status was unsuccessful.
  """
  if not response.is_success:
    raise_http_status(response)
  envelope = validate_envelope(response.text)
  if envelope['code'] != '200000':
    raise_code(envelope['code'], envelope.get('msg', ''), envelope)
  return envelope.get('data')
