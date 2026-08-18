"""Credential resolution and request signing, shared by the REST and WebSocket transports.

Kept as plain functions, not a client class: `HttpRpcClient` already holds a plain transport
client plus a `credentials` field directly, so there's nothing left for a stateful
authenticated client to own — these functions are called from `authed_request()`/the WS
login handshake to build a signature per call.
"""

from dataclasses import dataclass, field
import base64
import hashlib
import hmac
import os

from typed_core.exceptions import AuthError


@dataclass(frozen=True)
class Credentials:
  """Access key, secret and passphrase, shared by every authenticated transport on one client."""

  access_key: str
  secret_key: str = field(repr=False)
  passphrase: str = field(repr=False)


def resolve_credentials(
  access_key: str | None,
  secret_key: str | None,
  passphrase: str | None,
  *,
  public: bool,
) -> Credentials | None:
  """Resolve the one `Credentials` a client's REST and WebSocket transports share.

  A Bitget account is either Classic-mode or UTA-mode (see the classic account-upgrade
  endpoint in `spec/discovery.md`), never both at once, so one key only ever authenticates
  against the surface matching the account's actual mode — the caller picks which
  surface's methods to use, not the client. Called once, from the root client's `.new()`,
  not from each transport's own `.new()`, so REST and WS can't read the environment at
  different times and disagree.

  Args:
    access_key: Bitget access key; read from `BITGET_ACCESS_KEY` when omitted.
    secret_key: Bitget secret key; read from `BITGET_SECRET_KEY` when omitted.
    passphrase: Bitget API passphrase, set at key creation; read from `BITGET_PASSPHRASE`
      when omitted.
    public: Skip resolution entirely and return `None`, for a credential-free client.

  Raises:
    AuthError: `public` is false and any of the three credentials was neither passed nor
      found in the environment.
  """
  if public:
    return None
  access_key = access_key or os.environ.get('BITGET_ACCESS_KEY')
  secret_key = secret_key or os.environ.get('BITGET_SECRET_KEY')
  passphrase = passphrase or os.environ.get('BITGET_PASSPHRASE')
  if not access_key or not secret_key or not passphrase:
    raise AuthError(
      'No credentials: set BITGET_ACCESS_KEY/BITGET_SECRET_KEY/BITGET_PASSPHRASE, pass '
      'access_key/secret_key/passphrase, or build with `public=True` for the credential-free surface.'
    )
  return Credentials(access_key, secret_key, passphrase)


def sign(message: str, secret: str) -> str:
  """Base64-encoded HMAC-SHA256 of `message`, keyed by `secret` — Bitget signs with base64,
  not hex, on both REST and WebSocket.
  """
  digest = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
  return base64.b64encode(digest).decode()


def auth_headers(
  credentials: Credentials, *, timestamp: str, method: str, path: str, body: str | None
) -> dict[str, str]:
  """Build the signed headers for one REST request.

  Args:
    credentials: Access key, secret key and passphrase.
    timestamp: Millisecond epoch timestamp, as sent in `ACCESS-TIMESTAMP`.
    method: HTTP method, uppercased.
    path: The request path *including* its sorted, URL-encoded query string (e.g.
      `/api/v2/spot/public/symbols?symbol=BTCUSDT`), exactly as signed — build this first,
      then sign, then send; never sign a reconstruction of what was actually sent.
    body: The compact JSON body, exactly as sent, or `None` for no body.
  """
  prehash = f'{timestamp}{method.upper()}{path}{body or ""}'
  return {
    'ACCESS-KEY': credentials.access_key,
    'ACCESS-SIGN': sign(prehash, credentials.secret_key),
    'ACCESS-TIMESTAMP': timestamp,
    'ACCESS-PASSPHRASE': credentials.passphrase,
    'Content-Type': 'application/json',
  }


def ws_login_args(credentials: Credentials, *, timestamp: str) -> dict[str, str]:
  """Build the single `args` entry of a WebSocket `login` op.

  Args:
    credentials: Access key, secret key and passphrase.
    timestamp: Unix-**second** timestamp (not milliseconds — a real difference from the
      REST header), as sent alongside the signature.
  """
  prehash = f'{timestamp}GET/user/verify'
  return {
    'apiKey': credentials.access_key,
    'passphrase': credentials.passphrase,
    'timestamp': timestamp,
    'sign': sign(prehash, credentials.secret_key),
  }
