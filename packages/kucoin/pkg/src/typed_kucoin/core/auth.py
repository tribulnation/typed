"""KuCoin request signing, shared by the HTTP and WebSocket transports.

References:
  - [KuCoin authentication](https://www.kucoin.com/docs-new)
"""

from dataclasses import dataclass, field
import base64
import hashlib
import hmac
import os

from typed_core.exceptions import AuthError

KEY_VERSION = '2'
"""`KC-API-KEY-VERSION` for every key created since KuCoin's passphrase-encryption change —
there is no live case for the older `'1'` worth supporting."""


@dataclass(frozen=True)
class Credentials:
  """API key, secret and passphrase, shared by every authenticated transport on one client.

  Three fields, not the usual two: KuCoin signs the account passphrase itself with the API
  secret (see `auth_headers`), so both the passphrase and the secret are needed at sign time.
  """

  api_key: str
  api_secret: str = field(repr=False)
  api_passphrase: str = field(repr=False)


def resolve_credentials(
  api_key: str | None,
  api_secret: str | None,
  api_passphrase: str | None,
  *,
  public: bool,
) -> Credentials | None:
  """Resolve the one `Credentials` a client's HTTP and WebSocket transports share.

  Called once, from `KuCoin.new` (`kucoin.main`) — every transport's own `.new()` takes an
  already-resolved `Credentials | None` rather than resolving it themselves, so they can't
  read the environment at different times and disagree.

  Args:
    api_key: KuCoin API key; read from `KUCOIN_API_KEY` when omitted.
    api_secret: KuCoin API secret; read from `KUCOIN_API_SECRET` when omitted.
    api_passphrase: KuCoin API passphrase; read from `KUCOIN_API_PASSPHRASE` when omitted.
    public: Skip resolution entirely and return `None`, for a credential-free client.

  Raises:
    AuthError: `public` is false and any of the three was not passed or found in the
      environment.
  """
  if public:
    return None
  api_key = api_key or os.environ.get('KUCOIN_API_KEY')
  api_secret = api_secret or os.environ.get('KUCOIN_API_SECRET')
  api_passphrase = api_passphrase or os.environ.get('KUCOIN_API_PASSPHRASE')
  if not api_key or not api_secret or not api_passphrase:
    raise AuthError(
      'No credentials: set KUCOIN_API_KEY/KUCOIN_API_SECRET/KUCOIN_API_PASSPHRASE, pass '
      'api_key/api_secret/api_passphrase, or build with `public=True` for the '
      'credential-free surface.'
    )
  return Credentials(api_key, api_secret, api_passphrase)


def sign(secret: str, message: str) -> str:
  """Base64-encoded HMAC-SHA256 of `message`, keyed by `secret`."""
  digest = hmac.new(secret.encode(), message.encode(), hashlib.sha256).digest()
  return base64.b64encode(digest).decode()


def auth_headers(
  credentials: Credentials, *, timestamp: str, method: str, endpoint: str, body: str
) -> dict[str, str]:
  """Build the five `KC-API-*` headers for one signed request.

  Args:
    credentials: API key, secret and passphrase.
    timestamp: Millisecond timestamp, sent alongside the signature so KuCoin can reject
      stale requests; must match the timestamp folded into the signature.
    method: HTTP method, uppercase, exactly as sent.
    endpoint: Request path plus query string, unencoded, exactly as sent.
    body: Compact JSON body exactly as sent, or `''` for a body-less request.
  """
  message = f'{timestamp}{method}{endpoint}{body}'
  return {
    'KC-API-KEY': credentials.api_key,
    'KC-API-SIGN': sign(credentials.api_secret, message),
    'KC-API-TIMESTAMP': timestamp,
    'KC-API-PASSPHRASE': sign(credentials.api_secret, credentials.api_passphrase),
    'KC-API-KEY-VERSION': KEY_VERSION,
  }
