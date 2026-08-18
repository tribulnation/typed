"""Binance's response envelope and its mapping onto `typed_core` exceptions.

Success carries no wrapper: the raw JSON body *is* the result, for both REST and the WS
API. Failure is signaled by a status — an HTTP status for REST, an equivalent numbered
`status` field for the WS API — with an optional `{code, msg}` embedded in the body/`error`
refining why. `raise_error` is shared by both transports for exactly that reason.
"""

from typing_extensions import Any

from typed_core.exceptions import ApiError, AuthError, BadRequest, RateLimited

AUTH_CODES = frozenset({-1002, -1021, -1022, -2014, -2015})
"""UNAUTHORIZED, INVALID_TIMESTAMP (outside recvWindow), INVALID_SIGNATURE,
API_KEY_FORMAT_INVALID, REJECTED_MBX_KEY (bad key/IP/permissions) — from Binance's shared
`errors.md` error-code table.
"""

RATE_LIMIT_CODES = frozenset({-1003, -1015})
"""TOO_MANY_REQUESTS (request weight or IP ban), TOO_MANY_ORDERS."""


def raise_error(status: int, payload: Any):
  """Raise the `typed_core` exception matching one failed REST/WS API response.

  Args:
    status: The HTTP status (REST) or the WS API response's own `status` field — both
      follow the same 4XX/5XX conventions per Binance's docs.
    payload: The decoded error body — `{code, msg}` when Binance provided one, the raw
      body otherwise.

  Raises:
    AuthError: An auth-related embedded `code`, or status `401`.
    RateLimited: A rate-limit embedded `code`, or status `429` (rate limit), `418` (IP
      auto-ban), `403` (WAF rule violation — Binance's own docs call this "a rate limit
      violation or a security block", no dedicated exception fits better).
    BadRequest: Any other `4XX`.
    ApiError: Any other unsuccessful status — includes `5XX`, where Binance states the
      execution status is actually *unknown*, not a confirmed failure.
  """
  code = payload.get('code') if isinstance(payload, dict) else None
  if code in AUTH_CODES or status == 401:
    raise AuthError(status, payload)
  if code in RATE_LIMIT_CODES or status in (403, 418, 429):
    raise RateLimited(status, payload)
  if 400 <= status < 500:
    raise BadRequest(status, payload)
  raise ApiError(status, payload)
