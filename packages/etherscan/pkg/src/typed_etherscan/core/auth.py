"""Credential resolution for the Etherscan API key, plus the optional client-side rate
limit -- both read from `clients/etherscan/.env` in this checkout (`ETHERSCAN_API_KEY`,
`ETHERSCAN_RATE_LIMIT`), never printed or logged."""

import os

from typed_core.exceptions import AuthError
from typed_core.util import RateLimit


def resolve_api_key(api_key: str | None, *, public: bool) -> str | None:
  """Resolve the API key the HTTP transport authenticates with.

  Called once, from the root client's `.new()`.

  Args:
    api_key: Etherscan API key; read from `ETHERSCAN_API_KEY` when omitted.
    public: Skip resolution entirely and return `None`, for a credential-free client --
      only `usage.chain_list` is reachable then.

  Raises:
    AuthError: `public` is false and no key was passed or found in the environment.
  """
  if public:
    return None
  api_key = api_key or os.environ.get('ETHERSCAN_API_KEY')
  if not api_key:
    raise AuthError(
      'No credentials: set ETHERSCAN_API_KEY, pass api_key, or build with `public=True` '
      'for the credential-free surface (usage.chain_list only).'
    )
  return api_key


def resolve_rate_limit(rate_limit: int | None) -> RateLimit | None:
  """Resolve the client-side calls-per-second cap, read from `ETHERSCAN_RATE_LIMIT` when
  omitted.

  Etherscan's free tier enforces a strict per-second cap; a caller who sets neither the
  argument nor the environment variable gets no client-side cap at all -- only the
  `RateLimited` the venue itself raises, reactively, once the limit is already exceeded.

  Args:
    rate_limit: Maximum calls per second, or `None` to read `ETHERSCAN_RATE_LIMIT`.
  """
  if rate_limit is None:
    env_value = os.environ.get('ETHERSCAN_RATE_LIMIT')
    if env_value is not None:
      rate_limit = int(env_value)
  return RateLimit(rate_limit) if rate_limit is not None else None
