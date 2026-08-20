"""Credential resolution for Alchemy's `api-key-path` auth scheme.

The app API key (`ALCHEMY_API_KEY`) is required by every surface this client implements
in this pass -- Chain APIs, the enhanced `alchemy_*` JSON-RPC methods, NFT API v3,
Portfolio, Prices -- because the key is a literal path segment of the request URL itself,
not a header attached per request (`docs/spec/authoring.md` rule 9's `api-key-path`
scheme). There is no meaningful `public=True` build for those surfaces: without the key
there is no valid URL to construct at all, so unlike a per-request-signing venue this
client does not expose a public/authenticated split at the root -- see `spec/core.md`'s
Authentication section for the full reasoning.
"""

import os

from typed_core.exceptions import AuthError

from .util.paths import path_join


def resolve_api_key(api_key: str | None) -> str:
  """Resolve the one Alchemy app API key every REST/JSON-RPC surface needs.

  Args:
    api_key: Explicit key, checked before the environment.

  Raises:
    AuthError: No key was passed and `ALCHEMY_API_KEY` is not set.
  """
  if api_key is not None:
    return api_key
  value = os.environ.get('ALCHEMY_API_KEY')
  if not value:
    raise AuthError(
      'No credentials: set ALCHEMY_API_KEY, or pass `api_key=` to `Alchemy.new()`.'
    )
  return value


def api_key_url(base_url: str, api_key: str) -> str:
  """Append the resolved app API key as the final path segment of an Alchemy base URL.

  Args:
    base_url: Host and product path, e.g. `https://eth-mainnet.g.alchemy.com/v2`.
    api_key: Resolved app API key.
  """
  return path_join(base_url, api_key)
