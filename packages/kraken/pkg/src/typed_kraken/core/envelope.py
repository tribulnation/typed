"""Kraken Spot REST's response envelope, `{error, result}`, and its mapping onto
`typed_core` exceptions, per the venue's own categorized error reference.
"""

from typing_extensions import Any, NotRequired
import httpx

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited
from typed_core.validation import TypedDict, validator


class Envelope(TypedDict):
  """Every Spot REST response, public or private.

  A non-empty `error` array means failure, even though the HTTP status stays 200.
  """

  error: list[str]
  result: NotRequired[Any]


validate_envelope = validator(Envelope)

CATEGORY_EXCEPTIONS: dict[str, type[ApiError]] = {
  'EAPI': AuthError,
  'EAuth': AuthError,
  'EAccount': AuthError,
  'EGeneral': BadRequest,
  'ETrade': BadRequest,
  'EFunding': BadRequest,
  'EOrder': ApiError,
  'EService': ApiError,
  'EBM': ApiError,
}
"""Default exception per error category prefix (`<Category>:<Description>`), from
Kraken's own error categorization. Overridden by the substring lists below for messages
whose meaning cuts across categories (e.g. `EOrder:Rate limit exceeded`).
"""

RATE_LIMIT_SUBSTRINGS = (
  'Rate limit exceeded',
  'Too many requests',
  'Orders limit exceeded',
  'Domain rate limit exceeded',
  'Scheduled orders limit exceeded',
)
AUTH_SUBSTRINGS = (
  'Invalid key',
  'Invalid signature',
  'Invalid nonce',
  'Permission denied',
  'Temporary lockout',
)
BAD_REQUEST_SUBSTRINGS = (
  'Invalid price',
  'Tick size check failed',
  'Order minimum not met',
  'Cost minimum not met',
)


def raise_error(errors: list[str]):
  """Raise the `typed_core` exception matching Kraken's `error` array.

  Args:
    errors: The envelope's non-empty `error` array; only the first entry is inspected,
      matching Kraken's own convention of listing the primary failure first.

  Raises:
    AuthError: Key, signature, nonce, permission or lockout rejection.
    RateLimited: Request or order throttled.
    BadRequest: Malformed or out-of-range request parameters.
    ApiError: Any other category (order/service/business-logic failures).

  References:
    - [Error messages](https://docs.kraken.com/exchange/guides/general/errors)
  """
  message = errors[0]
  category = message.partition(':')[0]
  if any(s in message for s in RATE_LIMIT_SUBSTRINGS):
    raise RateLimited(errors)
  if any(s in message for s in AUTH_SUBSTRINGS):
    raise AuthError(errors)
  if any(s in message for s in BAD_REQUEST_SUBSTRINGS):
    raise BadRequest(errors)
  raise CATEGORY_EXCEPTIONS.get(category, ApiError)(errors)


def raise_http_status(response: httpx.Response):
  """Raise on a non-2xx HTTP status.

  Rare for Kraken -- it answers 200 even for most logical errors -- but edge/proxy
  failures (e.g. Cloudflare) still surface this way.

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
  """Return the envelope's `result`, raising on either failure discriminator.

  Args:
    response: The HTTP response to unwrap.

  Raises:
    ValidationError: The body was not JSON, or not a recognizable envelope.
    ApiError: The `error` array was non-empty, or the HTTP status was unsuccessful.
  """
  if not response.is_success:
    raise_http_status(response)
  envelope = validate_envelope(response.text)
  if envelope['error']:
    raise_error(envelope['error'])
  return envelope.get('result')
