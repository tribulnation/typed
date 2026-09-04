"""Credential resolution and HMAC signing for Coinbase Exchange (formerly Pro/GDAX), shared
by the HTTP and WebSocket Feed transports.

A Coinbase Exchange API key is a key/secret/passphrase triple, created in the Exchange (or
sandbox) UI — a wholly separate credential from the CDP API Key `typed_coinbase.core.auth`
signs for Coinbase App/Advanced Trade. Every private request is signed per-request with
HMAC-SHA256: `base64(HMAC-SHA256(base64_decode(secret), timestamp + method + path + body))`,
sent as the `CB-ACCESS-{KEY,SIGN,TIMESTAMP,PASSPHRASE}` headers (confirmed against the
official OpenAPI spec's `securitySchemes`: `cb-access-key`/`cb-access-sign`/
`cb-access-timestamp`/`cb-access-passphrase`, all `in: header` — HTTP header names are
case-insensitive, so the canonical `CB-ACCESS-*` casing used in prose is used here too).
WebSocket private channels sign a fixed string instead of the actual request, since a
subscribe message has no method/path/body of its own to bind to: `{timestamp}GET/users/self/verify`.
"""

from dataclasses import dataclass, field
import base64
import hashlib
import hmac
import os
import time

from typed_core.exceptions import AuthError


@dataclass(frozen=True)
class Credentials:
  """A Coinbase Exchange API key: key, secret, and passphrase, all three required to sign
  a request. Unrelated to `typed_coinbase.core.auth.Credentials` (the CDP API Key) — a
  client authenticated for Coinbase App/Advanced Trade carries no Exchange access at all.
  """

  key: str
  """`CB-ACCESS-KEY`, as shown once at key creation."""
  secret: str = field(repr=False)
  """The alphanumeric secret string, base64-decoded before use as the HMAC key — never the
  raw HMAC key itself."""
  passphrase: str = field(repr=False)
  """The passphrase chosen at key creation. Lost if forgotten — Exchange cannot recover it."""


def resolve_credentials(
  key: str | None, secret: str | None, passphrase: str | None, *, public: bool
) -> Credentials | None:
  """Resolve the one `Credentials` Exchange's HTTP and WebSocket transports share.

  Called once, from `Exchange.new()` — not from each transport's own construction, so HTTP
  and WebSocket can't read the environment at different times and disagree.

  Args:
    key: Exchange API key; read from `COINBASE_EXCHANGE_API_KEY` when omitted.
    secret: Exchange API secret; read from `COINBASE_EXCHANGE_API_SECRET` when omitted.
    passphrase: Exchange API passphrase; read from `COINBASE_EXCHANGE_PASSPHRASE` when omitted.
    public: Skip resolution entirely and return `None`, for a credential-free client.

  Raises:
    AuthError: `public` is false and no complete credential was passed or found in the
      environment.
  """
  if public:
    return None
  key = key or os.environ.get('COINBASE_EXCHANGE_API_KEY')
  secret = secret or os.environ.get('COINBASE_EXCHANGE_API_SECRET')
  passphrase = passphrase or os.environ.get('COINBASE_EXCHANGE_PASSPHRASE')
  if not key or not secret or not passphrase:
    raise AuthError(
      'No Exchange credentials: set COINBASE_EXCHANGE_API_KEY/COINBASE_EXCHANGE_API_SECRET/'
      'COINBASE_EXCHANGE_PASSPHRASE, pass key/secret/passphrase, or build with '
      '`exchange_public=True` for the credential-free surface.'
    )
  return Credentials(key, secret, passphrase)


def _sign(secret: str, prehash: str) -> str:
  """Base64-encoded HMAC-SHA256 signature of `prehash`, keyed by the base64-decoded secret."""
  key = base64.b64decode(secret)
  digest = hmac.new(key, prehash.encode(), hashlib.sha256).digest()
  return base64.b64encode(digest).decode()


def auth_headers(
  credentials: Credentials, *, method: str, path: str, body: str
) -> dict[str, str]:
  """Build the four `CB-ACCESS-*` headers for one signed HTTP request.

  Args:
    credentials: The Exchange API key to sign with.
    method: The HTTP method, uppercase.
    path: The request path plus query string, exactly as sent on the wire — signed and
      sent must be built from the same string, or the signature won't match. The signing
      string in the venue's own examples is built with no query string in the one example
      shown (`POST /orders`, no query params); this client assumes a query string is
      included when present, matching every third-party Exchange/Pro client reviewed, but
      that assumption is unverified against a live signed request — see `spec/core.md`.
    body: The exact JSON request body as sent, or `''` for a body-less request.
  """
  timestamp = f'{time.time():.6f}'
  prehash = f'{timestamp}{method.upper()}{path}{body}'
  return {
    'CB-ACCESS-KEY': credentials.key,
    'CB-ACCESS-SIGN': _sign(credentials.secret, prehash),
    'CB-ACCESS-TIMESTAMP': timestamp,
    'CB-ACCESS-PASSPHRASE': credentials.passphrase,
  }


def ws_auth_fields(credentials: Credentials) -> dict[str, str]:
  """Build the `signature`/`key`/`passphrase`/`timestamp` fields for a private WebSocket
  Feed subscribe message.

  Unlike the HTTP signature, this always signs the same fixed string
  (`{timestamp}GET/users/self/verify`) rather than the actual subscribe message — Exchange's
  WS auth binds to the connection, not to a specific request.
  """
  timestamp = f'{time.time():.6f}'
  prehash = f'{timestamp}GET/users/self/verify'
  return {
    'signature': _sign(credentials.secret, prehash),
    'key': credentials.key,
    'passphrase': credentials.passphrase,
    'timestamp': timestamp,
  }
