"""Typed async client for the Moralis API."""

from typed_core import (
  ApiError as ApiError,
  AuthError as AuthError,
  BadRequest as BadRequest,
  Error as Error,
  HttpClient as _HttpClient,
  LogicError as LogicError,
  NetworkError as NetworkError,
  RateLimited as RateLimited,
  ValidationError as ValidationError,
)

from .core import MORALIS_API_URL as _MORALIS_API_URL, Router, env_api_key
from .evm import Evm


class Moralis(Router):
  """Composite Moralis client."""
  evm: Evm
  """EVM API group."""

  @classmethod
  def new(
    cls, api_key: str | None = None, /, *,
    base_url: str = _MORALIS_API_URL,
    validate: bool = True,
    http: _HttpClient | None = None,
  ) -> 'Moralis':
    """Create a Moralis client.

    Args:
      api_key: Moralis API key. If omitted, falls back to `MORALIS_API_KEY`.
      base_url: Moralis API base URL override.
      validate: Validate responses by default.
      http: Shared HTTP client override.
    """
    return cls(
      base_url=base_url,
      api_key=env_api_key(api_key),
      validate=validate,
      http=http or _HttpClient(),
    )
