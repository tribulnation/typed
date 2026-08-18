"""Shared credential resolution. MEXC issues one key pair for both spot and futures
signing, so resolution is shared here; the signing itself differs per surface and lives
in `mexc.spot.core.auth`/`mexc.futures.core.auth`.
"""

from dataclasses import dataclass, field
import os

from typed_core.exceptions import AuthError


@dataclass(frozen=True)
class Credentials:
  """API key and secret, shared by every authenticated transport on one client."""

  api_key: str
  api_secret: str = field(repr=False)


def resolve_credentials(
  api_key: str | None, api_secret: str | None, *, public: bool
) -> Credentials | None:
  """Resolve the one `Credentials` every spot and futures transport shares.

  Called once, from the root client's `.new()` — not from each transport's own `.new()`,
  so spot and futures can't read the environment at different times and disagree.

  Args:
    api_key: MEXC access key; read from `MEXC_ACCESS_KEY` when omitted.
    api_secret: MEXC secret key; read from `MEXC_SECRET_KEY` when omitted.
    public: Skip resolution entirely and return `None`, for a credential-free client.

  Raises:
    AuthError: `public` is false and no credentials were passed or found in the environment.
  """
  if public:
    return None
  api_key = api_key or os.environ.get('MEXC_ACCESS_KEY')
  api_secret = api_secret or os.environ.get('MEXC_SECRET_KEY')
  if not api_key or not api_secret:
    raise AuthError(
      'No credentials: set MEXC_ACCESS_KEY/MEXC_SECRET_KEY, pass api_key/api_secret, '
      'or build with `public=True` for the credential-free surface.'
    )
  return Credentials(api_key, api_secret)
