"""Bitget-facing re-exports of `typed_core`'s exception hierarchy.

No Bitget-specific exception is needed: every venue error maps onto the shared hierarchy,
see `spec/core.md`'s Errors table.
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
