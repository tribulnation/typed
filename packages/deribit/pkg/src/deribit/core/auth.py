"""Credential resolution, JSON-RPC token exchange, and HMAC request signing — shared by
the HTTP and WebSocket transports.

Deribit documents three `public/auth` grant types: `client_credentials` (used here to
mint the default Bearer token, see `TokenCache`), `client_signature` (the opt-in
per-request HTTP signing this module's `sign`/`hmac_auth_header` implement — the exact
HTTP variant came from a since-404'd authentication guide rather than the OpenAPI spec
directly, but is now confirmed against a live signed `private/get_open_orders_by_currency`
call on testnet), and `refresh_token` (not used here: `TokenCache` re-authenticates from
scratch on expiry rather than refreshing).
"""

from typing_extensions import Awaitable, Callable, NotRequired, TypedDict as _TypedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import asyncio
import hashlib
import hmac
import os
import secrets
import time

from typed_core.exceptions import AuthError


@dataclass(frozen=True)
class Credentials:
  """Deribit `client_id`/`client_secret`, shared by every authenticated transport on one
  client."""

  client_id: str
  client_secret: str = field(repr=False)


def resolve_credentials(
  client_id: str | None,
  client_secret: str | None,
  *,
  public: bool,
  testnet: bool,
) -> Credentials | None:
  """Resolve the one `Credentials` a client's HTTP and WebSocket transports share.

  Called once, from `Deribit.new()` — not from each transport's own construction, so
  HTTP and WS can't read the environment at different times and disagree.

  Args:
    client_id: Deribit API client id; read from `{TEST_,}DERIBIT_CLIENT_ID` when omitted.
    client_secret: Deribit API client secret; read from `{TEST_,}DERIBIT_CLIENT_SECRET`
      when omitted.
    public: Skip resolution entirely and return `None`, for a credential-free client.
    testnet: Read the `TEST_`-prefixed environment variables instead of the mainnet ones.

  Raises:
    AuthError: `public` is false and no credentials were passed or found in the
      environment.
  """
  if public:
    return None
  prefix = 'TEST_DERIBIT' if testnet else 'DERIBIT'
  client_id = client_id or os.environ.get(f'{prefix}_CLIENT_ID')
  client_secret = client_secret or os.environ.get(f'{prefix}_CLIENT_SECRET')
  if not client_id or not client_secret:
    raise AuthError(
      f'No credentials: set {prefix}_CLIENT_ID/{prefix}_CLIENT_SECRET, pass '
      'client_id/client_secret, or build with `public=True` for the credential-free surface.'
    )
  return Credentials(client_id, client_secret)


def sign(message: str, secret: str) -> str:
  """Hex-encoded HMAC-SHA256 of `message`, keyed by `secret`."""
  return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


def hmac_auth_header(
  credentials: Credentials, *, method: str, uri: str, body: str
) -> str:
  """Build the `Authorization` header for one `client_signature`-signed HTTP request.

  Args:
    credentials: Client id and secret.
    method: HTTP method, upper-cased into the signed string.
    uri: The request path (e.g. `/api/v2/private/get_open_orders_by_currency`), exactly
      as sent — HTTP requests carry no query string here (`params` travels in the JSON
      body instead), so `uri` never has one.
    body: The request body, exactly as sent, or `''` for none.
  """
  timestamp = str(int(time.time() * 1000))
  nonce = secrets.token_hex(8)
  request_data = f'{method.upper()}\n{uri}\n{body}\n'
  string_to_sign = f'{timestamp}\n{nonce}\n{request_data}'
  signature = sign(string_to_sign, credentials.client_secret)
  return (
    f'deri-hmac-sha256 id={credentials.client_id},ts={timestamp},'
    f'nonce={nonce},sig={signature}'
  )


TOKEN_REFRESH_BUFFER = timedelta(seconds=30)
"""Refresh this long before `expires_in` elapses, so a cached token never goes stale
mid-request."""


class AuthResult(_TypedDict):
  """`result` of a successful `public/auth` call."""

  access_token: str
  refresh_token: NotRequired[str]
  expires_in: int
  scope: NotRequired[str]
  token_type: NotRequired[str]


@dataclass
class TokenCache:
  """Lazily fetches and caches one `public/auth` access token.

  Construct one per transport that needs it (HTTP and WebSocket each get their own) so
  neither's handshake blocks or races the other's.
  """

  credentials: Credentials
  _token: str | None = field(default=None, init=False, repr=False)
  _expires_at: datetime | None = field(default=None, init=False, repr=False)
  _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  async def get(
    self, authenticate: Callable[[Credentials], Awaitable[AuthResult]]
  ) -> str:
    """Return a live access token, authenticating first if none is cached or it expired.

    Args:
      authenticate: Calls `public/auth` with `grant_type=client_credentials` over
        whichever transport owns this cache, and returns its result.
    """
    async with self._lock:
      now = datetime.now(timezone.utc)
      if self._token is None or self._expires_at is None or now >= self._expires_at:
        result = await authenticate(self.credentials)
        self._token = result['access_token']
        self._expires_at = (
          now + timedelta(seconds=result['expires_in']) - TOKEN_REFRESH_BUFFER
        )
      return self._token
