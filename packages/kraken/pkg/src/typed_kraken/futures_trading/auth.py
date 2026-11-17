"""Kraken Futures credentials and signing: the REST `Authent` header and the
WebSocket challenge. Futures keys are separate from Spot keys and created on the
Futures site (or its demo environment).
"""

from dataclasses import dataclass, field
import base64
import hashlib
import hmac
import os

from typed_core.exceptions import AuthError


@dataclass(frozen=True)
class FuturesCredentials:
  """Kraken Futures API key pair, shared by the signed HTTP and WebSocket transports."""

  api_key: str
  private_key: str = field(repr=False)
  """Base64-encoded API secret, used to sign; never sent over the wire."""


def resolve_futures_credentials(
  api_key: str | None, private_key: str | None, *, public: bool
) -> FuturesCredentials | None:
  """The credentials of a Futures client, from the arguments or the environment.

  Args:
    api_key: Futures API key; read from `KRAKEN_FUTURES_API_KEY` when omitted.
    private_key: Futures API secret; read from `KRAKEN_FUTURES_PRIVATE_KEY` when omitted.
    public: Skip resolution and return `None`, for a credential-free client.

  Raises:
    AuthError: `public` is false and no credentials were passed or found.
  """
  if public:
    return None
  api_key = api_key or os.environ.get('KRAKEN_FUTURES_API_KEY')
  private_key = private_key or os.environ.get('KRAKEN_FUTURES_PRIVATE_KEY')
  if not api_key or not private_key:
    raise AuthError(
      'No Futures credentials: set KRAKEN_FUTURES_API_KEY/KRAKEN_FUTURES_PRIVATE_KEY, '
      'pass api_key/private_key, or build with `public=True`.'
    )
  return FuturesCredentials(api_key, private_key)


def hmac_digest(message: bytes, private_key: str) -> str:
  """Base64 HMAC-SHA512 of SHA-256(`message`), keyed by the base64-decoded secret."""
  digest = hashlib.sha256(message).digest()
  mac = hmac.new(base64.b64decode(private_key), digest, hashlib.sha512)
  return base64.b64encode(mac.digest()).decode()


def sign_request(*, path: str, post_data: str, nonce: str, private_key: str) -> str:
  """The `Authent` header of a signed Futures REST request.

  Args:
    path: The request path; a leading `/derivatives` is not signed, so
      `/derivatives/api/v3/sendorder` signs as `/api/v3/sendorder`.
    post_data: The exact URL-encoded parameters sent (query string or body).
    nonce: The `Nonce` header sent with the request, or `''` when none is sent.
    private_key: Base64-encoded API secret.

  References:
    - [Futures REST authentication](https://docs.kraken.com/api/docs/guides/futures-rest)
  """
  endpoint = path.removeprefix('/derivatives')
  return hmac_digest(f'{post_data}{nonce}{endpoint}'.encode(), private_key)


def sign_challenge(challenge: str, private_key: str) -> str:
  """The `signed_challenge` of a private Futures WebSocket subscription.

  Args:
    challenge: The `message` of the venue's `challenge` event.
    private_key: Base64-encoded API secret.

  References:
    - [Futures WebSocket challenge](https://docs.kraken.com/api/docs/futures-api/websocket/challenge)
  """
  return hmac_digest(challenge.encode(), private_key)
