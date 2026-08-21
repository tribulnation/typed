"""Credential resolution and CDP API Key JWT signing, shared by the HTTP and WebSocket
transports.

A CDP API Key is one ECDSA (P-256, ES256) or Ed25519 (EdDSA) keypair, authenticated by a
short-lived (2-minute) JWT signed per request — not a cached token, and not HMAC request
signing. The HTTP transport binds each JWT's `uri` claim to that request's exact method
and path; the WebSocket transport carries the same JWT, without a `uri` claim, as a
`jwt` field on the subscribe message itself.
"""

from typing_extensions import Literal
from dataclasses import dataclass, field
from datetime import timedelta
import base64
import json
import os
import secrets
import time

from cryptography.hazmat.primitives.asymmetric import ec, ed25519
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from .exc import AuthError

JWT_TTL = timedelta(minutes=2)
"""CDP API Key JWTs are rejected past this lifetime — matches the venue's own limit, not
a client-chosen margin, so there is nothing to refresh: a fresh JWT is built per request."""


@dataclass(frozen=True)
class Credentials:
  """A CDP API Key, shared by every authenticated transport on one client."""

  key_name: str
  """`organizations/{org_id}/apiKeys/{key_id}`, from the CDP portal."""
  private_key: str = field(repr=False)
  """Either an EC (P-256) private key in PEM form, or an Ed25519 private key as the
  portal's base64-encoded 64-byte seed+public-key export."""


def resolve_credentials(
  key_name: str | None, private_key: str | None, *, public: bool
) -> Credentials | None:
  """Resolve the one `Credentials` a client's HTTP and WebSocket transports share.

  Called once, from `Coinbase.new()` — not from each transport's own construction, so
  HTTP and WebSocket can't read the environment at different times and disagree.

  Args:
    key_name: CDP API Key name; read from `COINBASE_API_KEY_NAME` when omitted.
    private_key: CDP API Key private key; read from `COINBASE_PRIVATE_KEY` when omitted.
    public: Skip resolution entirely and return `None`, for a credential-free client.

  Raises:
    AuthError: `public` is false and no credentials were passed or found in the environment.
  """
  if public:
    return None
  key_name = key_name or os.environ.get('COINBASE_API_KEY_NAME')
  private_key = private_key or os.environ.get('COINBASE_PRIVATE_KEY')
  if not key_name or not private_key:
    raise AuthError(
      'No credentials: set COINBASE_API_KEY_NAME/COINBASE_PRIVATE_KEY, pass '
      'key_name/private_key, or build with `public=True` for the credential-free surface.'
    )
  return Credentials(key_name, private_key)


def _b64url(data: bytes) -> str:
  return base64.urlsafe_b64encode(data).rstrip(b'=').decode()


_Key = ec.EllipticCurvePrivateKey | ed25519.Ed25519PrivateKey


def _load_key(private_key: str) -> tuple[_Key, Literal['ES256', 'EdDSA']]:
  """Load whichever key format the CDP portal exported this key in.

  A PEM-encoded string is an EC (P-256) key, signed as `ES256`; anything else is taken
  as the portal's base64-encoded 64-byte Ed25519 export (32-byte seed + 32-byte public
  key), signed as `EdDSA`.
  """
  if private_key.lstrip().startswith('-----BEGIN'):
    key = load_pem_private_key(private_key.encode(), password=None)
    if not isinstance(key, ec.EllipticCurvePrivateKey):
      raise AuthError(
        f'Unsupported PEM private key type {type(key).__name__}: CDP API Keys sign '
        'with an EC (P-256) key, not this one.'
      )
    return key, 'ES256'
  else:
    seed = base64.b64decode(private_key)[:32]
    return ed25519.Ed25519PrivateKey.from_private_bytes(seed), 'EdDSA'


def _sign(key: _Key, alg: Literal['ES256', 'EdDSA'], signing_input: bytes) -> bytes:
  """Raw JWS signature bytes for `signing_input`.

  An EC key's signature comes back DER-encoded from `cryptography` and is re-packed into
  JWS's fixed-width `r || s` form; Ed25519 signatures are already in the form JWS expects.
  """
  if isinstance(key, ec.EllipticCurvePrivateKey):
    der = key.sign(signing_input, ec.ECDSA(SHA256()))
    r, s = decode_dss_signature(der)
    return r.to_bytes(32, 'big') + s.to_bytes(32, 'big')
  else:
    return key.sign(signing_input)


def _build_jwt(credentials: Credentials, *, uri: str | None) -> str:
  key, alg = _load_key(credentials.private_key)
  now = int(time.time())
  header = {
    'alg': alg,
    'kid': credentials.key_name,
    'nonce': secrets.token_hex(16),
    'typ': 'JWT',
  }
  payload = {
    'sub': credentials.key_name,
    'iss': 'cdp',
    'nbf': now,
    'exp': now + int(JWT_TTL.total_seconds()),
  }
  if uri is not None:
    payload['uri'] = uri
  signing_input = f'{_b64url(json.dumps(header, separators=(",", ":")).encode())}.{_b64url(json.dumps(payload, separators=(",", ":")).encode())}'
  signature = _sign(key, alg, signing_input.encode())
  return f'{signing_input}.{_b64url(signature)}'


def auth_headers(
  credentials: Credentials, *, method: str, host: str, path: str
) -> dict[str, str]:
  """Build the `Authorization` header for one signed HTTP request.

  Args:
    credentials: The CDP API Key to sign with.
    method: The HTTP method, exactly as sent.
    host: The request host, e.g. `api.coinbase.com` — no scheme, no path.
    path: The request path, without the query string.
  """
  token = _build_jwt(credentials, uri=f'{method} {host}{path}')
  return {'Authorization': f'Bearer {token}'}


def ws_jwt(credentials: Credentials) -> str:
  """Build the `jwt` field sent on a WebSocket subscribe message to a private channel.

  Unlike the HTTP JWT, this carries no `uri` claim — Coinbase validates it once, at
  subscribe time, against the connection rather than a specific request.
  """
  return _build_jwt(credentials, uri=None)
