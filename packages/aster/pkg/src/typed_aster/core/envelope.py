"""The Binance-style response envelope shared by futures, spot, prediction and Aster Chain
REST, and its mapping onto `typed_core` exceptions.

Success carries no wrapper: the JSON body is the result. Failure is an HTTP `4XX`/`5XX`
with a `{code, msg}` body. A few write endpoints (`noop`, agent/builder management,
sub-accounts) answer success as `{"code": 200, "msg": "success"}`, which is returned as
the result, never raised.
"""

from typing_extensions import Any
import json

import httpx

from typed_core.exceptions import (
  ApiError,
  AuthError,
  BadRequest,
  RateLimited,
  ValidationError,
)

AUTH_CODES = frozenset({-1002, -1021, -1022, -2014, -2015, -4225, -5050})
"""UNAUTHORIZED, INVALID_TIMESTAMP, INVALID_SIGNATURE, BAD_API_KEY_FMT, REJECTED_MBX_KEY,
`-4225` Nonce Expired, and `-5050` DEPOSIT_REQUIRED (signed calls are refused until the
main wallet has deposited)."""

AUTH_MESSAGES = ('signature check failed', 'no agent found')
"""Messages Aster sends under the catch-all code `-1000` UNKNOWN that are really
authentication failures (observed live: a signature over the wrong `chainId`, and an
agent-signed call before the account's first deposit)."""

RATE_LIMIT_CODES = frozenset({-1003, -1015})
"""TOO_MANY_REQUESTS, TOO_MANY_ORDERS."""


def decode(content: bytes) -> Any:
  """Decode a JSON body."""
  return json.loads(content)


def raise_error(status: int, payload: Any):
  """Raise the `typed_core` exception matching one failed response.

  Args:
    status: The HTTP status.
    payload: The decoded body — `{code, msg}` when Aster provided one.

  Raises:
    AuthError: An authentication `code` or `-1000` message, or status `401`.
    RateLimited: A rate-limit `code`, or status `429` (rate limit), `418` (IP ban) or
      `403` (WAF limit).
    BadRequest: Any other `4XX`.
    ApiError: Anything else, including `5XX`. A `503` means the execution status is
      unknown, not that the request failed.
  """
  code = payload.get('code') if isinstance(payload, dict) else None
  msg = str(payload.get('msg', '')).lower() if isinstance(payload, dict) else ''
  if (
    code in AUTH_CODES
    or status == 401
    or (code == -1000 and any(m in msg for m in AUTH_MESSAGES))
  ):
    raise AuthError(status, payload)
  if code in RATE_LIMIT_CODES or status in (403, 418, 429):
    raise RateLimited(status, payload)
  if 400 <= status < 500:
    raise BadRequest(status, payload)
  raise ApiError(status, payload)


def is_error(payload: Any) -> bool:
  """Whether a `2XX` body is really an error: exactly `{code, msg}` with a code other
  than the success code `200`."""
  return (
    isinstance(payload, dict)
    and set(payload) == {'code', 'msg'}
    and payload['code'] != 200
  )


def unwrap(response: httpx.Response) -> Any:
  """Return the decoded result of a response, raising on failure. An empty `2XX` body
  (documented for builder management and a no-op `assetExchange`) is `None`.

  Raises:
    ValidationError: The body is not JSON.
    ApiError: The call failed (see `raise_error`).
  """
  if response.is_success and not response.content.strip():
    return None
  try:
    payload = decode(response.content)
  except ValueError:
    if response.is_success:
      raise ValidationError(f'Expected a JSON body, got: {response.text[:200]!r}')
    payload = response.text
  if not response.is_success:
    raise_error(response.status_code, payload)
  if is_error(payload):
    raise_error(response.status_code, payload)
  return payload
