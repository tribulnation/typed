"""Moralis credential resolution -- a single bearer API key, no request signing."""

import os

from typed_core.exceptions import AuthError


def env_api_key(api_key: str | None = None) -> str:
  """Return the explicit API key or load `MORALIS_API_KEY`.

  Args:
    api_key: Explicit API key override.

  Raises:
    AuthError: No `api_key` was given and `MORALIS_API_KEY` is unset.
  """
  if api_key is not None:
    return api_key
  try:
    return os.environ['MORALIS_API_KEY']
  except KeyError as exc:
    raise AuthError(
      401,
      {
        'error': 'missing_api_key',
        'message': 'Either provide `api_key` or set MORALIS_API_KEY.',
      },
    ) from exc
