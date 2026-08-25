"""Bitget-facing re-exports of `typed_core`'s exception hierarchy, plus `AccountModeMismatch`,
the one Bitget-specific exception: every other venue error maps onto the shared hierarchy,
see `spec/core.md`'s Errors table.
"""

from typing_extensions import Any, Literal

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


class AccountModeMismatch(BadRequest):
  """An endpoint for one account mode was called while the account is in the other.

  Bitget's Classic and Unified (UTA) account APIs are mutually exclusive per account: a
  Classic-only endpoint rejects a Unified account and vice versa.
  """

  def __init__(self, expected: Literal['classic', 'uta'], code: str, msg: str, payload: Any):
    self.expected = expected
    """The account mode the called endpoint actually requires."""
    super().__init__(code, msg, payload)


__all__ = [
  'Error',
  'NetworkError',
  'ValidationError',
  'ApiError',
  'BadRequest',
  'AuthError',
  'RateLimited',
  'LogicError',
  'AccountModeMismatch',
]
