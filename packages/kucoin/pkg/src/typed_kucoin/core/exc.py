"""KuCoin exceptions — a plain re-export of `typed_core.exceptions`.

Every KuCoin error code (see `envelope.py`) maps onto one of these; none of them needed a
venue-specific subclass.
"""

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
]
