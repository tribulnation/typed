"""Response envelopes and their mapping onto `typed_core` exceptions.

Two families share nothing but HTTP:

- **Trading API**: success is a bare JSON body with a `2XX` status; failure is a proper
  HTTP status with `{code, message, details?}`, where `code` is one of a stable,
  documented enum. The same `{op: "error", code, message}` codes arrive over the
  WebSocket. Mapping is by `code`, falling back on the HTTP status for an unknown one.
- **Public backends** (per-chain backend, Backend Global, pricing): success is a bare
  JSON body; failure is `{"error": "..."}`, `{"type": "error", "message": "..."}`, or
  Express's HTML page for an unknown route. Mapping is by HTTP status, except that the
  per-chain backend also sends `{"type": "error", ...}` under a `200`: that is a
  `BadRequest`.

A `RateLimited` always ends its `args` with the seconds the `Retry-After` header asks to
wait (`None` when there is none, as over the WebSocket): `typed_core.RateLimited` has no
field for it.

References:
  - [Trading API errors](https://docs.gains.trade/developer/trading-api/errors)
"""

from typing_extensions import Any, Mapping, NoReturn
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json

import httpx

from .exc import ApiError, AuthError, BadRequest, RateLimited, ValidationError

AUTH_CODES = frozenset(
  {
    'UNAUTHENTICATED',
    'INVALID_SIGNATURE',
    'TIMESTAMP_OUT_OF_WINDOW',
    'NONCE_REUSED',
    'AGENT_UNKNOWN',
    'API_KEY_UNKNOWN',
    'AGENT_NOT_DELEGATED',
    'AGENT_EXPIRED',
    'AGENT_REVOKED',
    'SCOPE_READ_ONLY',
    'SCOPE_MARKET_NOT_ALLOWED',
    'SCOPE_LEVERAGE_EXCEEDED',
    'SCOPE_SPEND_CAP_EXCEEDED',
    'TRADER_MISMATCH',
    'TRADER_NOT_IN_BETA',
  }
)
"""Codes rejecting the credential, signature, delegation or agent scope (HTTP 401/403)."""

RATE_LIMIT_CODES = frozenset({'RATE_LIMITED'})
"""Codes throttling the request (HTTP 429, with `Retry-After` and `details.scope`)."""

SERVER_CODES = frozenset({'INTERNAL', 'UPSTREAM_UNAVAILABLE', 'NOT_READY'})
"""Codes for a server-side failure; the request itself may be fine to retry."""

BAD_REQUEST_CODES = frozenset(
  {
    'VALIDATION_ERROR',
    'CHAIN_NOT_FOUND',
    'CHAIN_READ_ONLY',
    'MARKET_NOT_FOUND',
    'ORDER_NOT_FOUND',
    'POSITION_NOT_FOUND',
    'AGENT_NOT_FOUND',
    'NOT_FOUND',
    'IDEMPOTENCY_CONFLICT',
    'ORDER_NOT_MODIFIABLE',
    'PRECISION_ERROR',
    'LEVERAGE_OUT_OF_RANGE',
    'SIZE_BELOW_MINIMUM',
    'MARKET_CLOSED',
    'COLLATERAL_NOT_SUPPORTED',
    'SIMULATION_REVERTED',
    'SUBMISSION_MISMATCH',
    'UNSUPPORTED',
    'TOO_MANY_PREPARED_ORDERS',
  }
)
"""Codes rejecting the request itself."""


def decode(response: httpx.Response) -> Any:
  """The JSON body of a successful response, or `None` when it is empty.

  Raises:
    ValidationError: The body is not JSON.
  """
  if not response.content:
    return None
  try:
    return json.loads(response.content)
  except ValueError:
    raise ValidationError(
      f'Expected a JSON body, got {response.headers.get("content-type")!r}: '
      f'{response.text[:200]!r}'
    ) from None


def retry_after(response: httpx.Response) -> float | None:
  """The seconds a response's `Retry-After` header asks to wait: delay-seconds or an HTTP
  date (RFC 9110). `None` when the header is absent or unreadable."""
  value = response.headers.get('Retry-After')
  if value is None:
    return None
  try:
    return max(0.0, float(value))
  except ValueError:
    pass
  try:
    when = parsedate_to_datetime(value)
  except (TypeError, ValueError):
    return None
  if when.tzinfo is None:
    when = when.replace(tzinfo=timezone.utc)
  return max(0.0, (when - datetime.now(timezone.utc)).total_seconds())


def raise_status(status: int, *args: Any, retry_after: float | None = None) -> NoReturn:
  """Raise the `typed_core` exception matching an unsuccessful HTTP status.

  Args:
    status: The HTTP status.
    args: The exception's arguments.
    retry_after: The `Retry-After` delay, in seconds, appended to a `RateLimited`'s
      arguments.

  Raises:
    AuthError: Status `401` or `403`.
    RateLimited: Status `429`.
    BadRequest: Any other `4XX` status.
    ApiError: Any other status.
  """
  if status in (401, 403):
    raise AuthError(*args)
  if status == 429:
    raise RateLimited(*args, retry_after)
  if 400 <= status < 500:
    raise BadRequest(*args)
  raise ApiError(*args)


def raise_code(
  *,
  code: str,
  message: str,
  payload: Any,
  status: int | None = None,
  retry_after: float | None = None,
) -> NoReturn:
  """Raise the `typed_core` exception matching a Trading API error `code`.

  Args:
    code: The error code, e.g. `AGENT_NOT_DELEGATED`.
    message: The error message.
    payload: The whole error object, `details` included, attached for the caller.
    status: The HTTP status, deciding the class of a code this mapping doesn't know.
      `None` over the WebSocket.
    retry_after: The `Retry-After` delay, in seconds, appended to a `RateLimited`'s
      arguments; `None` over the WebSocket.

  Raises:
    AuthError: Credential, signature, delegation or scope rejection.
    RateLimited: Throttled; `args` is `(code, message, payload, retry_after)`.
    BadRequest: The request itself was rejected.
    ApiError: A server-side failure, or an unknown code without a status.
  """
  if code in AUTH_CODES:
    raise AuthError(code, message, payload)
  if code in RATE_LIMIT_CODES:
    raise RateLimited(code, message, payload, retry_after)
  if code in BAD_REQUEST_CODES:
    raise BadRequest(code, message, payload)
  if code in SERVER_CODES or status is None:
    raise ApiError(code, message, payload)
  raise_status(status, code, message, payload, retry_after=retry_after)


def is_trading_error(value: Any) -> bool:
  """Whether `value` is a Trading API error object: `{code: str, message: str, ...}`."""
  return (
    isinstance(value, Mapping)
    and isinstance(value.get('code'), str)
    and isinstance(value.get('message'), str)
  )


def trading_result(response: httpx.Response) -> Any:
  """The decoded body of a Trading API response, raising on failure.

  Raises:
    AuthError, RateLimited, BadRequest, ApiError: The status is unsuccessful; mapped by
      the body's `code` when it carries one, else by status.
    ValidationError: A successful body is not JSON.
  """
  if response.is_success:
    return decode(response)
  try:
    payload: Any = json.loads(response.content)
  except ValueError:
    payload = response.text
  delay = retry_after(response)
  if is_trading_error(payload):
    raise_code(
      code=payload['code'],
      message=payload['message'],
      payload=payload,
      status=response.status_code,
      retry_after=delay,
    )
  raise_status(response.status_code, response.status_code, payload, retry_after=delay)


def typed_error_message(payload: Any) -> str | None:
  """The message of a `{"type": "error", "message": "..."}` body, else `None`.

  The per-chain backend answers a malformed path parameter with this shape under a `200`
  status (`/user-trading-variables/{bad}`), and a transient `500` with the same shape. The
  only success body with a top-level `type` is pricing's `{"type": "success", ...}`, which
  this never matches.
  """
  if (
    isinstance(payload, Mapping)
    and payload.get('type') == 'error'
    and isinstance(payload.get('message'), str)
  ):
    return payload['message']
  return None


def public_error_message(payload: Any) -> str | None:
  """The message of a public backend error body, `{"error": "..."}` or
  `{"type": "error", "message": "..."}`, else `None`."""
  if isinstance(payload, Mapping) and isinstance(payload.get('error'), str):
    return payload['error']
  return typed_error_message(payload)


def public_result(response: httpx.Response) -> Any:
  """The decoded body of a public backend response, raising on failure.

  Raises:
    AuthError, RateLimited, BadRequest, ApiError: The status is unsuccessful, mapped by
      status, carrying the error message (or the raw body when there is none).
    BadRequest: A successful status carries a `{"type": "error", "message": ...}` body,
      the backend's answer to a malformed input.
    ValidationError: A successful body is not JSON.
  """
  if response.is_success:
    payload = decode(response)
    message = typed_error_message(payload)
    if message is not None:
      raise BadRequest(response.status_code, message)
    return payload
  try:
    payload = json.loads(response.content)
  except ValueError:
    payload = response.text
  message = public_error_message(payload)
  raise_status(
    response.status_code,
    response.status_code,
    payload if message is None else message,
    retry_after=retry_after(response),
  )


def unwrap(payload: Any, key: str | None) -> Any:
  """`payload[key]` for an endpoint whose success wraps its value in one key, else `payload`.

  Raises:
    ValidationError: `payload` lacks `key`.
  """
  if key is None:
    return payload
  if not isinstance(payload, Mapping) or key not in payload:
    raise ValidationError(f'Expected a {{"{key}": ...}} envelope, got {payload!r:.200}')
  return payload[key]
