"""Bitget's REST response envelope and its mapping onto `typed_core` exceptions.

Identical across Classic v2 and UTA v3, confirmed live against both. See `spec/core.md`'s
Envelope and Errors sections for the source of every code below.
"""

from typing_extensions import Any, Literal, NotRequired
import httpx

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited
from typed_core.validation import TypedDict, validator

from .exc import AccountModeMismatch


class Envelope(TypedDict):
  """Every response is wrapped `{code, msg, requestTime, data}`.

  `code == "00000"` means success — a string, not an int — even though the HTTP status
  stays 200 on most embedded-code errors.
  """

  code: str
  msg: str
  requestTime: int
  data: NotRequired[Any]


validate_envelope = validator(Envelope)

ACCOUNT_MODE_CODES: dict[str, Literal['classic', 'uta']] = {
  '40084': 'classic',
  '40085': 'uta',
}
"""Endpoint called under the wrong account mode, keyed to the mode it actually requires —
confirmed live for both codes."""

AUTH_CODES = frozenset(
  {
    '40001',
    '40002',
    '40003',
    '40005',
    '40006',
    '40008',
    '40009',
    '40010',
    '40011',
    '40012',
    '40014',
    '40016',
    '40018',
    '40037',
  }
)
"""Missing/invalid key, secret, signature, passphrase, timestamp, permission or IP binding —
from Bitget's own error-code table, confirmed live for `40006`."""

RATE_LIMIT_CODES = frozenset({'1001'})
"""Request too frequent / throttled."""

BAD_REQUEST_CODES = frozenset({'40017', '40019', '40034', '400172', '40707', '40709'})
"""Malformed or missing request parameters — confirmed live for `400172`."""


def raise_code(code: str, msg: str, payload: Any):
  """Raise the `typed_core` exception matching a non-`"00000"` embedded error code.

  Args:
    code: Bitget's own error code.
    msg: Bitget's own error message.
    payload: The full envelope, attached to the exception for debugging.

  Raises:
    AuthError: Credential, signature, permission or IP-binding rejection.
    RateLimited: Request throttled by the venue.
    AccountModeMismatch: Endpoint called under the wrong account mode.
    BadRequest: Malformed request parameters.
    ApiError: Any other non-`"00000"` code.
  """
  if code in AUTH_CODES:
    raise AuthError(code, msg, payload)
  if code in RATE_LIMIT_CODES:
    raise RateLimited(code, msg, payload)
  if code in ACCOUNT_MODE_CODES:
    raise AccountModeMismatch(ACCOUNT_MODE_CODES[code], code, msg, payload)
  if code in BAD_REQUEST_CODES:
    raise BadRequest(code, msg, payload)
  raise ApiError(code, msg, payload)


def raise_http_status(response: httpx.Response):
  """Raise the `typed_core` exception matching a non-2xx HTTP status.

  Bitget sends some embedded error codes (e.g. an account-mode mismatch) with a non-2xx
  HTTP status rather than the usual `200` + `code != "00000"` shape, so a JSON body
  carrying its own `code` is classified by that code, the same as `raise_code`, rather than
  by HTTP status alone.

  Args:
    response: The unsuccessful HTTP response.

  Raises:
    AuthError: Status `401`/`403`, or an embedded code classified as such.
    RateLimited: Status `429`, or an embedded code classified as such.
    AccountModeMismatch: An embedded code for the wrong account mode.
    BadRequest: Any other `4xx` status, or an embedded code classified as such.
    ApiError: Any other unsuccessful status, or an embedded code classified as such.
  """
  try:
    payload: Any = response.json()
  except ValueError:
    payload = response.text
  if isinstance(payload, dict) and isinstance(payload.get('code'), str):
    raise_code(payload['code'], payload.get('msg', ''), payload)
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
    ApiError: The embedded `code` was not `"00000"`, or the HTTP status was unsuccessful.
  """
  if not response.is_success:
    raise_http_status(response)
  envelope = validate_envelope(response.text)
  if envelope['code'] != '00000':
    raise_code(envelope['code'], envelope.get('msg', ''), envelope)
  return envelope.get('data')
