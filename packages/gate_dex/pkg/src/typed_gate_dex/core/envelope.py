"""The Gate DEX response envelope and its mapping onto `typed_core` exceptions."""

from typing_extensions import Any, NotRequired
import httpx

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited
from typed_core.validation import TypedDict, validator


class Envelope(TypedDict):
  """Every action's response, `{code, msg|message, data}`. `code == 0` means success.

  The message key differs by action: `trade.swap.*` answers `message`, every other action
  (and the gateway's own errors) `msg`. Extra keys are kept: `market.pair.liquidity.list`
  puts `page` beside `data`.
  """

  code: int
  """`0` on success; any other value is Gate's error code."""
  msg: NotRequired[str]
  """Message, on every action but `trade.swap.*`, and on the gateway's own errors."""
  message: NotRequired[str]
  """Message, on `trade.swap.*` actions."""
  data: NotRequired[Any]
  """The action's result."""


validate_envelope = validator(Envelope)
"""Parse and validate a response body as an `Envelope`, raising `ValidationError` when it is
not one. Checks the envelope only, never the shape of `data`."""

AUTH_CODES = frozenset(
  {
    10001,
    10002,
    10003,
    10005,
    10008,
    10101,
    10102,
    10103,
    10111,
    10112,
    10113,
    10121,
    10122,
    10161,
  }
)
"""Gateway rejections of the authentication headers, from the published error table: missing
`X-API-Key`/`X-Timestamp`/`X-Signature`/`X-Request-Id` (10001-10003, 10005), signature
mismatch or failed verification (10008, 10103), timestamp outside ±30 s (10101), key not
found (10102), IP allowlist (10111-10113), malformed or replayed `X-Request-Id`
(10121-10122), missing user claims (10161)."""

RATE_LIMIT_CODES = frozenset({10131, 10132, 10133})
"""Rate limited: globally, per API key, or per action."""

BAD_REQUEST_CODES = frozenset(
  {
    10004,
    20001,
    20002,
    20005,
    20009,
    21001,
    21003,
    31101,
    31102,
    31106,
    31107,
    31108,
    31112,
    31801,
    41001,
    41003,
    41102,
  }
)
"""Codes describing a problem with the request's own input. From the published tables:
missing `action` (10004), missing or mistyped params (20001, 20002, 31801, 41001),
unsupported chain (21001, 41003), candle count over the limit (21003), quote amount above
the maximum, below the minimum, too small or invalid (31101, 31102, 31106, 31107),
unsupported token or cross-chain pair (31108, 31112), token not found (41102). Observed
live but unpublished: 20005 (`period invalid` on `market.candles`, `The current chain is
not supported` on `trade.swap.gasprice`) and 20009 (`JSON parse error`).

Codes whose meaning is market state, an internal failure, or ambiguous between sources
(21002) stay `ApiError`. So does 31000, observed live on `trade.swap.build` and absent from
every published table: it relays whatever error the upstream quote service returned
(`Quote service returned error: {"code":20002,...}`), so its own code says nothing about
whose fault the failure is."""


def message(envelope: Envelope) -> str:
  """The envelope's message, under whichever key this action uses."""
  return envelope.get('msg') or envelope.get('message') or ''


def raise_code(code: int, msg: str, payload: Any):
  """Raise the `typed_core` exception matching a non-zero envelope `code`.

  Args:
    code: Gate's own error code.
    msg: Gate's own error message.
    payload: The full envelope, attached for debugging.

  Raises:
    AuthError: Authentication headers rejected.
    RateLimited: Request throttled.
    BadRequest: The request's own input was rejected.
    ApiError: Any other non-zero code.
  """
  if code in AUTH_CODES:
    raise AuthError(code, msg, payload)
  if code in RATE_LIMIT_CODES:
    raise RateLimited(code, msg, payload)
  if code in BAD_REQUEST_CODES:
    raise BadRequest(code, msg, payload)
  raise ApiError(code, msg, payload)


def raise_failure(response: httpx.Response):
  """Raise for an unsuccessful HTTP status, by envelope `code` when the body carries one.

  The gateway answers its own rejections with an HTTP error status *and* an envelope
  (`401 {"code": 10102, "msg": "key not found"}`); the code is the more specific signal, so
  it wins. A body with no envelope (APISIX's `404 Route Not Found`, a proxy's HTML page)
  falls back to the status alone.

  Args:
    response: The unsuccessful HTTP response.

  Raises:
    AuthError: Auth code, or status `401`/`403`.
    RateLimited: Rate-limit code, or status `429`.
    BadRequest: Bad-request code, or any other `4xx` status.
    ApiError: Any other failure.
  """
  try:
    payload: Any = response.json()
  except ValueError:
    payload = response.text
  if (
    isinstance(payload, dict)
    and isinstance(code := payload.get('code'), int)
    and code != 0
  ):
    raise_code(code, payload.get('msg') or payload.get('message') or '', payload)
  status = response.status_code
  if status in (401, 403):
    raise AuthError(status, payload)
  if status == 429:
    raise RateLimited(status, payload)
  if 400 <= status < 500:
    raise BadRequest(status, payload)
  raise ApiError(status, payload)


def unwrap(response: httpx.Response, *, keep_envelope: bool = False) -> Any:
  """Return a response's `data`, or its whole envelope, raising on any failure.

  Args:
    response: The HTTP response to unwrap.
    keep_envelope: Return the validated envelope instead of its `data`, for an action
      that carries something the caller needs beside `data`.

  Raises:
    ValidationError: A successful response whose body is not a recognizable envelope.
    ApiError: A non-zero `code`, or an unsuccessful HTTP status.
  """
  if not response.is_success:
    raise_failure(response)
  envelope = validate_envelope(response.content)
  if envelope['code'] != 0:
    raise_code(envelope['code'], message(envelope), envelope)
  if keep_envelope:
    return envelope
  return envelope.get('data')
