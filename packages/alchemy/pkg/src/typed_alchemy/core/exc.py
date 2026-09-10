"""This client's exceptions: the shared `typed_core` ones, plus the one place an Alchemy
URL has to be kept out of an error message.
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

REDACTED = '[REDACTED]'
"""Stands in for a removed credential. A placeholder rather than a deletion, so the URL
stays legible and a reader can see that something was taken out."""


def without_api_key(error: NetworkError, api_key: str) -> NetworkError:
  """Rebuild `error` with the app API key replaced by `REDACTED`.

  Alchemy carries the key as the final path segment of every URL this client builds
  (`core.auth.api_key_url`), and `typed_core.HttpClient` names the URL it failed on, so
  the key would otherwise be part of the raised message and travel wherever that string
  goes: a caller's own `except NetworkError` handler, a traceback, a retry log.

  Raise the result `from error.__cause__`, never `from error`: the original carries the
  key in its own message, and keeping it in the chain puts it straight back into the
  traceback this exists to keep clean.

  Args:
    error: The error the transport raised.
    api_key: The resolved app API key to remove.
  """
  args = tuple(
    arg.replace(api_key, REDACTED) if isinstance(arg, str) else arg for arg in error.args
  )
  return NetworkError(*args)


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
