"""The main API's `{code, message}` envelope and its mapping onto `typed_core` exceptions.

Most responses are `{"code": 200, "message"?: ..., ...payload}`, the payload flattened beside
`code`; some (`/`, `/info`, `withdrawalDelay`, `l1Metadata`, ...) carry no `code` at all.
Failure is therefore "`code` present and not 200", never "`code` absent". Errors arrive as
HTTP 400/401 with the same `{code, message}` body, HTTP 429/405 for rate limits, and
CloudFront HTML for blocked paths, so the body may not even be JSON. The same `{code,
message}` pair also comes back inside WebSocket `{"error": {...}}` frames.

Every exception raised here carries `(code_or_status, message, payload)`, where a code-less
WebSocket error frame's first argument is its raw `code` value (`None`, or a non-numeric
string). Only one raised from a venue business code (`raise_code`) is marked as such, so
`error_code` never mistakes an HTTP status for one. An HTTP 5xx is always a plain
`ApiError`, even when its body carries a code.
"""

from typing_extensions import Any, NoReturn
import httpx

from .exc import ApiError, AuthError, BadRequest, RateLimited

CODE_OK = 200

AUTH_CODES = frozenset({20013, 21108, 21109, 21120, 21504})
"""Invalid auth token (20013, observed live), public key not registered (21108), API key
not found (21109), invalid signature (21120), failed L1 signature (21504)."""

RATE_LIMIT_CODES = frozenset({21506, 23000, 23001, 23002, 23003, 23004, 30009, 30010})
"""Too many pending transactions (21506), too many requests/subscriptions/accounts/
connections/withdrawals (23000-23004), too many WebSocket messages (30009), too many
in-flight WebSocket messages (30010)."""

BAD_REQUEST_CODES = frozenset(
  {20001, 23201, 23202, 30000, 30001, 30002, 30003, 30005, 30007}
)
"""Invalid parameter, including a missing token (20001), the testnet faucet's refusals
(23201: the address's portfolio is worth 100 USD or more; 23202: no faucet in this
environment), and the WebSocket framing errors: invalid JSON/type (30000/30001),
not/already subscribed (30002/30003), invalid channel or data (30005/30007)."""

BAD_REQUEST_FAMILIES = range(21100, 22500)
"""Account, pool, collateral, block, transaction, market, order, asset and deleverage
business rules (211xx-224xx): the request was well-formed but refused as invalid."""

INVALID_NONCE = 21104
"""`invalid nonce`: the nonce manager refetches instead of retrying blindly."""

VENUE_CODE = 'lighter_code'
"""Attribute `raise_code` sets on the exceptions it raises, holding the business code."""


def parse_code(value: object) -> int | None:
  """A wire `code` as an integer: an integer, or a string of digits; `None` otherwise."""
  if isinstance(value, bool):
    return None
  if isinstance(value, int):
    return value
  if isinstance(value, str) and value.strip().lstrip('-').isdigit():
    return int(value)
  return None


def raise_code(
  code: int, message: str, payload: Any, *, server_error: bool = False
) -> NoReturn:
  """Raise the `typed_core` exception matching a non-200 business code.

  Args:
    code: Lighter's own error code.
    message: Lighter's own error message.
    payload: The full error body, attached for debugging.
    server_error: The code came with an HTTP 5xx: the request's outcome is unknown, so it
      is a plain `ApiError` whatever the code, never a refusal.

  Raises:
    AuthError: Rejected token, key or signature.
    RateLimited: Throttled request, connection or subscription.
    BadRequest: Invalid parameter or refused business rule.
    ApiError: Any other code, or any code on an HTTP 5xx.
  """
  if server_error:
    error: ApiError = ApiError(code, message, payload)
  elif code in AUTH_CODES:
    error = AuthError(code, message, payload)
  elif code in RATE_LIMIT_CODES:
    error = RateLimited(code, message, payload)
  elif code in BAD_REQUEST_CODES or code in BAD_REQUEST_FAMILIES:
    error = BadRequest(code, message, payload)
  else:
    error = ApiError(code, message, payload)
  setattr(error, VENUE_CODE, code)
  raise error


def error_code(error: ApiError) -> int | None:
  """The Lighter business code of an exception raised by `raise_code`; `None` for any other
  (an HTTP status error, a code-less WebSocket error, a locally raised one)."""
  code = getattr(error, VENUE_CODE, None)
  return code if isinstance(code, int) else None


def raise_error_frame(error: object, payload: Any) -> NoReturn:
  """Raise for a WebSocket `{"error": {code, message}}` frame.

  A frame whose `code` is missing or not an integer carries no business code: its outcome
  is unknown, so it raises a plain `ApiError` that `error_code` reads as `None`.

  Args:
    error: The frame's `error` value.
    payload: The whole frame, attached for debugging.

  Raises:
    ApiError: Always; the subclass `raise_code` picks when the code is an integer.
  """
  raw = error.get('code') if isinstance(error, dict) else None
  message = str(error.get('message', '')) if isinstance(error, dict) else str(error)
  code = parse_code(raw)
  if code is None:
    raise ApiError(raw, message, payload)
  raise_code(code, message, payload)


def http_message(payload: Any) -> str:
  """A human-readable message for a code-less error body."""
  if isinstance(payload, dict):
    return str(payload.get('message') or payload.get('error') or '')
  return str(payload)


def raise_http_status(response: httpx.Response, payload: Any) -> NoReturn:
  """Raise for an unsuccessful response whose body carries no business code.

  Raises:
    AuthError: Status 401.
    RateLimited: Status 429, or 405 (Lighter's firewall throttle).
    BadRequest: Any other 4xx.
    ApiError: 5xx, or CloudFront's HTML 403 for a blocked path.
  """
  status = response.status_code
  message = http_message(payload)
  if status == 401:
    raise AuthError(status, message, payload)
  if status in (429, 405):
    raise RateLimited(status, message, payload)
  if status == 403:
    raise ApiError(status, 'Request blocked (CloudFront)', payload)
  if 400 <= status < 500:
    raise BadRequest(status, message, payload)
  raise ApiError(status, message, payload)


def unwrap(response: httpx.Response) -> Any:
  """Return a response's JSON body, raising on an error status or a non-200 `code`.

  The body is returned whole, `code`/`message` included: the payload sits beside them,
  not under a wrapper key, so there is nothing to extract. An HTTP 5xx is a plain
  `ApiError` even when its body carries a business code: the server failed, so whether the
  request took effect is unknown.

  Raises:
    ApiError: The embedded `code` was not 200, or the HTTP status was unsuccessful.
  """
  try:
    payload: Any = response.json() if response.content else {}
  except ValueError:
    payload = response.text[:500]
  if (
    isinstance(payload, dict) and (code := parse_code(payload.get('code'))) is not None
  ):
    if code != CODE_OK:
      message = str(payload.get('message', ''))
      raise_code(code, message, payload, server_error=response.status_code >= 500)
  if not response.is_success:
    raise_http_status(response, payload)
  return payload
