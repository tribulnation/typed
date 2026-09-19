"""Shared exceptions and the placeholder used for redacted credentials."""

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

REDACTED = '[REDACTED]'
"""Stands in for a removed credential. A placeholder rather than a deletion, so the URL
stays legible and a reader can see that something was taken out."""


def without_api_key(error: NetworkError, api_key: str) -> NetworkError:
  """Return a copy with the configured key removed; raise it with `from None`.

  Kept for callers using the original helper. Client requests additionally protect
  URL overrides, transport logs and API errors through `core.privacy`.
  """
  from .privacy import Redactor

  redactor = Redactor.new(api_key=api_key, base_url='')
  return NetworkError(*redactor.value(error.args))


__all__ = [
  'REDACTED',
  'without_api_key',
  'Error',
  'NetworkError',
  'ValidationError',
  'ApiError',
  'BadRequest',
  'AuthError',
  'RateLimited',
  'LogicError',
]
