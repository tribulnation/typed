"""Credential resolution, request signing, and nonce/token management for Kraken
Spot's HMAC-SHA512 REST auth and its WebSocket token exchange.
"""

from typing_extensions import Awaitable, Callable, NotRequired, TypedDict as _TypedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import asyncio
import base64
import hashlib
import hmac
import os
import time

from typed_core.exceptions import AuthError


@dataclass(frozen=True)
class Credentials:
  """Kraken Spot API key pair, shared by the HTTP and WebSocket transports."""

  api_key: str
  private_key: str = field(repr=False)
  """Base64-encoded private key, used to sign requests; never sent over the wire."""


def resolve_credentials(
  api_key: str | None, private_key: str | None, *, public: bool
) -> Credentials | None:
  """Resolve the one `Credentials` Spot's HTTP and WebSocket transports share.

  Called once, from the root client's `.new()`.

  Args:
    api_key: Kraken API key; read from `KRAKEN_API_KEY` when omitted.
    private_key: Kraken private (secret) key; read from `KRAKEN_PRIVATE_KEY` when omitted.
    public: Skip resolution entirely and return `None`, for a credential-free client.

  Raises:
    AuthError: `public` is false and no credentials were passed or found in the environment.
  """
  if public:
    return None
  api_key = api_key or os.environ.get('KRAKEN_API_KEY')
  private_key = private_key or os.environ.get('KRAKEN_PRIVATE_KEY')
  if not api_key or not private_key:
    raise AuthError(
      'No credentials: set KRAKEN_API_KEY/KRAKEN_PRIVATE_KEY, pass api_key/private_key, '
      'or build with `public=True` for the credential-free surface.'
    )
  return Credentials(api_key, private_key)


@dataclass
class NonceGenerator:
  """A strictly-increasing nonce, as Kraken's REST auth requires -- it rejects a nonce
  less than or equal to the last one accepted for the same key. Backed by the current
  millisecond timestamp, bumped by one whenever two calls land in the same millisecond.
  """

  _last: int = field(default=0, init=False, repr=False)
  _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  async def next(self) -> int:
    """The next nonce, guaranteed greater than every nonce returned before it."""
    async with self._lock:
      now = int(time.time() * 1000)
      self._last = now if now > self._last else self._last + 1
      return self._last


def sign(path: str, nonce: int, encoded_body: str, private_key: str) -> str:
  """Kraken Spot's `API-Sign` header value.

  Args:
    path: The request path, e.g. `/0/private/Balance` -- no query string, Spot private
      endpoints take every parameter in the body.
    nonce: The nonce included in `encoded_body`, hashed in separately per Kraken's
      scheme (`SHA256(nonce + body)`, not `SHA256(body)` alone).
    encoded_body: The exact form-urlencoded body being sent, `nonce` included.
    private_key: Base64-encoded private key.

  References:
    - [Spot REST Authentication](https://docs.kraken.com/exchange/guides/rest/authentication)
  """
  digest = hashlib.sha256(f'{nonce}{encoded_body}'.encode()).digest()
  mac = hmac.new(base64.b64decode(private_key), path.encode() + digest, hashlib.sha512)
  return base64.b64encode(mac.digest()).decode()


TOKEN_REFRESH_BUFFER = timedelta(seconds=30)
"""Refresh the WebSocket token this long before its ~900s lifetime elapses, so a
cached token never goes stale mid-request.
"""


class AuthResult(_TypedDict):
  """Result of `GetWebSocketsToken`, adapted to `access_token`/`expires_in` so
  `TokenCache` stays shape-agnostic about which venue call produced it.
  """

  access_token: str
  expires_in: int
  refresh_token: NotRequired[str]


@dataclass
class TokenCache:
  """Lazily fetches and caches the WebSocket auth token obtained from
  `GetWebSocketsToken` -- a private REST call, signed like any other. WebSocket
  private channels/methods send this token per-request instead of per-message signing.

  Construct one per private connection -- don't share a single instance across two
  physically separate sockets, so neither's fetch blocks or races the other's.
  """

  _token: str | None = field(default=None, init=False, repr=False)
  _expires_at: datetime | None = field(default=None, init=False, repr=False)
  _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  async def get(self, fetch: Callable[[], Awaitable[AuthResult]]) -> str:
    """Return a live token, fetching or refreshing first if needed.

    Args:
      fetch: Calls `GetWebSocketsToken` and returns its result -- supplied by the
        owning socket, bound to the Spot HTTP client that actually knows how to sign
        the call (see `transport/http.py`'s `get_ws_token`).
    """
    async with self._lock:
      now = datetime.now(timezone.utc)
      if self._token is None or self._expires_at is None or now >= self._expires_at:
        result = await fetch()
        self._token = result['access_token']
        self._expires_at = (
          now + timedelta(seconds=result['expires_in']) - TOKEN_REFRESH_BUFFER
        )
      return self._token
