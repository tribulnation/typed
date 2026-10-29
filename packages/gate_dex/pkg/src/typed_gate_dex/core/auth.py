"""Credential resolution and Gate DEX request signing."""

from dataclasses import dataclass, field
import base64
import hashlib
import hmac
import os
import uuid

from typed_core.exceptions import AuthError

API_KEY_ENV = 'GATE_DEX_API_KEY'
"""Environment variable holding the API Key (AK)."""
SECRET_KEY_ENV = 'GATE_DEX_SECRET_KEY'
"""Environment variable holding the Secret Key (SK)."""

SIGN_PATH = '/api/v1/dex'
"""Request path every signature covers. The docs fix it to this literal, independent of the
URL actually requested."""


@dataclass(frozen=True)
class Credentials:
  """API Key (AK) and Secret Key (SK) issued by the Gate DEX developer console."""

  api_key: str
  """API Key (AK), sent as `X-API-Key`."""
  api_secret: str = field(repr=False)
  """Secret Key (SK), the HMAC key; never sent, and kept out of `repr`."""


def resolve_credentials(api_key: str | None, api_secret: str | None) -> Credentials:
  """Resolve the credentials every Gate DEX request needs; no action is public.

  Args:
    api_key: API Key (AK); read from `GATE_DEX_API_KEY` when omitted.
    api_secret: Secret Key (SK); read from `GATE_DEX_SECRET_KEY` when omitted.

  Raises:
    AuthError: Either value was neither passed nor found in the environment.
  """
  api_key = api_key or os.environ.get(API_KEY_ENV)
  api_secret = api_secret or os.environ.get(SECRET_KEY_ENV)
  if not api_key or not api_secret:
    raise AuthError(
      f'No credentials: pass api_key/api_secret or set {API_KEY_ENV}/{SECRET_KEY_ENV}. '
      'Every Gate DEX action requires them.'
    )
  return Credentials(api_key, api_secret)


def prehash(timestamp: int, body: bytes) -> bytes:
  """Build the signed message: `<X-Timestamp><requestPath><rawBody>`, nothing in between.

  Args:
    timestamp: Epoch milliseconds, exactly as sent in `X-Timestamp`.
    body: The JSON body, exactly the bytes sent.
  """
  return str(timestamp).encode() + SIGN_PATH.encode() + body


def sign(message: bytes, secret: str) -> str:
  """Base64-encoded HMAC-SHA256 of `message`, keyed by the UTF-8 bytes of `secret`.

  The secret is used as-is, never base64-decoded first: the console-issued format contains
  a `.`, so it is not base64.
  """
  digest = hmac.new(secret.encode(), message, hashlib.sha256).digest()
  return base64.b64encode(digest).decode()


def auth_headers(
  credentials: Credentials, *, timestamp: int, body: bytes
) -> dict[str, str]:
  """Build the four authentication headers for one request.

  `X-Request-Id` is a fresh UUIDv4 per call: the venue rejects a reused id (`10122`), and
  a UUIDv4 satisfies both the docs' format (letters, digits, `-`, `_`) and Gate's own
  skills' stricter "standard UUIDv4". It is not part of the signature.

  Args:
    credentials: API Key and Secret Key.
    timestamp: Epoch milliseconds; the venue rejects one outside ±30 s of its clock.
    body: The JSON body, exactly the bytes sent.
  """
  return {
    'X-API-Key': credentials.api_key,
    'X-Timestamp': str(timestamp),
    'X-Signature': sign(prehash(timestamp, body), credentials.api_secret),
    'X-Request-Id': str(uuid.uuid4()),
  }
