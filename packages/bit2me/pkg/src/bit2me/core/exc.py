"""Bit2Me exceptions: a re-export of the shared `typed-core` hierarchy plus the
HTTP-status/WS-close-code mapping documented in `spec/core.md`'s Errors table.

Bit2Me's error signal is HTTP status alone on the `http` surface (error bodies vary
enough in shape across endpoints — sometimes `errorPayload`, sometimes a nested
`data: {errorCode, errorType}` — that nothing but the status code is a reliable
discriminator) and WS close codes on `trading_ws`/`crypto_ws`/`explorer_ws`. Neither
needs a venue-specific exception subclass; every signal maps onto a shared one.
"""

from typing_extensions import Any
import httpx

from typed_core.exceptions import (
  Error,
  NetworkError,
  ValidationError,
  ApiError,
  BadRequest,
  AuthError,
  RateLimited,
  LogicError,
)

__all__ = [
  'Error',
  'NetworkError',
  'ValidationError',
  'ApiError',
  'BadRequest',
  'AuthError',
  'RateLimited',
  'LogicError',
  'raise_http_status',
]


def raise_http_status(response: httpx.Response):
  """Raise the `typed_core` exception matching a non-2xx HTTP response, per
  `spec/core.md`'s Errors table.

  Args:
    response: The failed response. Its body is decoded as JSON when possible, since
      Bit2Me's error payloads usually are, falling back to raw text otherwise.
  """
  payload: Any
  try:
    payload = response.json()
  except Exception:
    payload = response.text
  status = response.status_code
  if status in (401, 403):
    raise AuthError(status, payload)
  elif status == 400:
    raise BadRequest(status, payload)
  elif status in (429, 418):
    raise RateLimited(status, payload)
  else:
    raise ApiError(status, payload)
