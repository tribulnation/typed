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
"""Stands in for a removed credential. A placeholder rather than a deletion, so the URL
stays legible and a reader can see that something was taken out."""


def without_listen_key(error: NetworkError, listen_key: str) -> NetworkError:
  """Rebuild `error` with the private-stream listenKey replaced by `REDACTED`.

  A listenKey is a session token for one account's private user-data stream, and it is
  embedded in the socket URL path because connecting with it *is* the subscription.
  `typed_core.ws.Socket` names the URL it failed to connect to, so the key would
  otherwise be part of the raised message and travel wherever that string goes: a
  caller's own `except NetworkError` handler, a traceback, a retry log.

  Raise the result `from error.__cause__`, never `from error`: the original carries the
  key in its own message, and keeping it in the chain puts it straight back into the
  traceback this exists to keep clean.

  Args:
    error: The error the transport raised.
    listen_key: The live listenKey to remove.
  """
  args = tuple(
    arg.replace(listen_key, REDACTED) if isinstance(arg, str) else arg for arg in error.args
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
