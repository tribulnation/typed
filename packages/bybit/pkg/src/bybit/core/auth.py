"""Bybit v5 request signing, shared by the HTTP and WebSocket transports.

References:
  - [Bybit v5 authentication](https://bybit-exchange.github.io/docs/v5/guide)
"""

from dataclasses import dataclass, field
import hashlib
import hmac
import os

from typed_core.exceptions import AuthError

RECV_WINDOW = '5000'
"""Default `X-BAPI-RECV-WINDOW`, in milliseconds."""


@dataclass(frozen=True)
class Credentials:
  """Bybit API key and secret, shared by every authenticated transport on one client."""

  api_key: str
  api_secret: str = field(repr=False)


def resolve_credentials(
  api_key: str | None,
  api_secret: str | None,
  *,
  public: bool,
) -> Credentials | None:
  """Resolve the one `Credentials` a client's HTTP and WebSocket transports share.

  Called once, from `Bybit.new` (`bybit.main`) — `Http.new` and `Ws.new` each take an
  already-resolved `Credentials | None` rather than resolving it themselves, so the two
  transports can't read the environment at different times and disagree.

  Args:
    api_key: Bybit API key; read from `BYBIT_API_KEY` when omitted.
    api_secret: Bybit API secret; read from `BYBIT_API_SECRET` when omitted.
    public: Skip resolution entirely and return `None`, for a credential-free client.

  Raises:
    AuthError: `public` is false and no credentials were passed or found in the
      environment.
  """
  if public:
    return None
  api_key = api_key or os.environ.get('BYBIT_API_KEY')
  api_secret = api_secret or os.environ.get('BYBIT_API_SECRET')
  if not api_key or not api_secret:
    raise AuthError(
      'No credentials: set BYBIT_API_KEY/BYBIT_API_SECRET, pass api_key/api_secret, '
      'or build with `public=True` for the credential-free Market surface.'
    )
  return Credentials(api_key, api_secret)


def hmac_sha256(secret: str, message: str) -> str:
  """Hex-encoded HMAC-SHA256 of `message`, keyed by `secret`."""
  return hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()


def rest_message(
  *,
  timestamp: str,
  api_key: str,
  recv_window: str = RECV_WINDOW,
  payload: str = '',
) -> str:
  """Build the exact string a REST request's `X-BAPI-SIGN` is computed over.

  `payload` is the URL-encoded query string for a `GET` request, or the compact JSON
  body for a `POST` request — whichever was actually sent, byte for byte.

  Args:
    timestamp: Millisecond timestamp, as sent in `X-BAPI-TIMESTAMP`.
    api_key: The caller's API key.
    recv_window: Millisecond validity window, as sent in `X-BAPI-RECV-WINDOW`.
    payload: Query string (`GET`) or compact JSON body (`POST`).
  """
  return f'{timestamp}{api_key}{recv_window}{payload}'


def rest_headers(
  credentials: Credentials,
  *,
  timestamp: str,
  recv_window: str = RECV_WINDOW,
  payload: str = '',
) -> dict[str, str]:
  """Build the four `X-BAPI-*` headers for one signed REST request.

  Args:
    credentials: API key and secret.
    timestamp: Millisecond timestamp.
    recv_window: Millisecond validity window.
    payload: Query string (`GET`) or compact JSON body (`POST`), matching `rest_message`.
  """
  message = rest_message(
    timestamp=timestamp,
    api_key=credentials.api_key,
    recv_window=recv_window,
    payload=payload,
  )
  return {
    'X-BAPI-API-KEY': credentials.api_key,
    'X-BAPI-TIMESTAMP': timestamp,
    'X-BAPI-RECV-WINDOW': recv_window,
    'X-BAPI-SIGN': hmac_sha256(credentials.api_secret, message),
  }


def ws_auth_args(credentials: Credentials, *, expires: int) -> list:
  """Build the `args` of a WebSocket `{"op": "auth"}` frame.

  Args:
    credentials: API key and secret.
    expires: Millisecond timestamp the signature is valid until; must be in the future.
  """
  signature = hmac_sha256(credentials.api_secret, f'GET/realtime{expires}')
  return [credentials.api_key, expires, signature]
