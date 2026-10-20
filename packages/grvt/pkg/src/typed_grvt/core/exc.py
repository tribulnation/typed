"""Exceptions raised by the GRVT client: the shared `typed_core` hierarchy, as-is."""

from typed_core.exceptions import (
  ApiError,
  AuthError,
  BadRequest,
  Error,
  LogicError,
  NetworkError,
  RateLimited,
  ValidationError,
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
