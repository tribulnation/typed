"""This client's exceptions: the shared `typed_core` ones, plus the one place a live
listenKey has to be kept out of an error message.
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
"""Stands in for a removed credential, so a URL stays legible after redaction."""


def without_listen_key(error: NetworkError, listen_key: str) -> NetworkError:
  """Rebuild `error` with the user-data listenKey replaced by `REDACTED`.

  The listenKey is embedded in the socket URL (`/ws/<listenKey>`), and
  `typed_core.ws.Socket` names the URL it failed to connect to. Raise the result
  `from error.__cause__`, never `from error`, so the key stays out of the traceback too.

  Args:
    error: The error the transport raised.
    listen_key: The live listenKey to remove.
  """
  args = tuple(
    arg.replace(listen_key, REDACTED) if isinstance(arg, str) else arg
    for arg in error.args
  )
  return NetworkError(*args)


__all__ = [
  'REDACTED',
  'without_listen_key',
  'Error',
  'NetworkError',
  'ValidationError',
  'ApiError',
  'BadRequest',
  'AuthError',
  'RateLimited',
  'LogicError',
]
