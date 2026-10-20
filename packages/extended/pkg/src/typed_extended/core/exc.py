"""Re-exports of the shared `typed_core` exception hierarchy.

Every Extended error signal (HTTP status, envelope `error.code`, WebSocket handshake
status) maps onto one of these; see `envelope.py` for the table.
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
