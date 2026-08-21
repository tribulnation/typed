"""Re-exports of the shared exception hierarchy this client raises. No venue-specific
exception is needed -- every failure this client distinguishes maps onto one of these."""

from typed_core.exceptions import (
  NetworkError, ValidationError, ApiError, AuthError, RateLimited, LogicError, BadRequest, Error,
)

__all__ = [
  'NetworkError', 'ValidationError', 'ApiError', 'AuthError', 'RateLimited', 'LogicError',
  'BadRequest', 'Error',
]
