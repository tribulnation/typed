"""Bit2Me authentication.

Three unrelated schemes, one per WS surface plus the shared HTTP one — see
`spec/core.md`'s Authentication section:

- `http` (Crypto API, Embed API, Trading Spot REST): per-request HMAC-SHA512 signing.
- `trading_ws`: a token minted by an `http`-signed call to `POST /v1/signin/apikey`,
  then sent once as the WS `authenticate` frame. `mint_ws_token` lives here rather than
  in `transport/ws/trading.py` since it's built entirely from this file's own
  primitives (`Credentials`, `auth_headers`) plus a bare `HttpClient` call — no
  WS-specific state involved.
- `crypto_ws`: none of the above — the raw API key or a JWT, sent unsigned as the first
  frame. Handled directly in `transport/ws/crypto.py`; nothing to share here.

`explorer_ws` needs no authentication at all.
"""

import base64
import hashlib
import hmac
import os
import time
from dataclasses import dataclass, field

from typed_core.exceptions import AuthError
from typed_core.http import HttpClient

from .exc import raise_http_status


@dataclass(frozen=True)
class Credentials:
  """A Bit2Me API key pair."""

  api_key: str
  api_secret: str = field(repr=False)


def resolve_credentials(
  api_key: str | None, api_secret: str | None, *, public: bool
) -> Credentials | None:
  """Resolve credentials once, from the root client's `.new()`.

  Args:
    api_key: Explicit API key, overriding `BIT2ME_API_KEY`.
    api_secret: Explicit API secret, overriding `BIT2ME_SECRET_KEY`.
    public: When `True`, missing credentials resolve to `None` (public-only client)
      rather than raising.

  Raises:
    AuthError: `public` is `False` and no credentials were found, in either the
      explicit arguments or the environment.
  """
  api_key = api_key or os.environ.get('BIT2ME_API_KEY')
  api_secret = api_secret or os.environ.get('BIT2ME_SECRET_KEY')
  if api_key and api_secret:
    return Credentials(api_key, api_secret)
  if public:
    return None
  raise AuthError(
    'No credentials: pass `api_key`/`api_secret`, set BIT2ME_API_KEY/BIT2ME_SECRET_KEY, or build with `public=True`'
  )


def message_to_sign(nonce: str, path: str, body: str | None = None) -> str:
  """Build the string Bit2Me expects signed: `nonce:path`, or `nonce:path:body` when
  there's a body. Never append the `:` separator for an absent/empty body."""
  message = f'{nonce}:{path}'
  if body:
    message += f':{body}'
  return message


def sign(message: str, secret: str) -> str:
  """Bit2Me's two-step signature: SHA-256 the message, HMAC-SHA512 the digest bytes
  (not the message itself), base64-encode the result."""
  digest = hashlib.sha256(message.encode()).digest()
  signature = hmac.new(secret.encode(), digest, hashlib.sha512).digest()
  return base64.b64encode(signature).decode()


def auth_headers(
  credentials: Credentials, *, nonce: str, path: str, body: str | None = None
) -> dict[str, str]:
  """Build the `X-API-KEY`/`x-nonce`/`api-signature` headers for one signed request.

  Args:
    credentials: The key pair to sign with.
    nonce: Current Unix epoch milliseconds, as a string; must be within 5 seconds of
      Bit2Me's clock.
    path: The exact request path (plus query string, if any) being signed.
    body: The exact compact-serialized JSON body being sent, or `None`/empty for a
      bodyless request. Sign the bytes that actually get sent, never a reconstruction.
  """
  message = message_to_sign(nonce, path, body)
  return {
    'X-API-KEY': credentials.api_key,
    'x-nonce': nonce,
    'api-signature': sign(message, credentials.api_secret),
  }


async def mint_ws_token(credentials: Credentials, *, base_url: str) -> str:
  """Mint the one-minute token `trading_ws` authenticates with, via an `http`-signed
  `POST /v1/signin/apikey`.

  A bare `HttpClient` is used directly rather than the full `HttpRpcClient` transport,
  since this is one self-contained signed call with nothing to unwrap beyond
  `accessToken.token` — building a whole transport for it would be circular (the
  `trading_ws` transport needs this before it has anything else).
  """
  nonce = str(int(time.time() * 1000))
  path = '/v1/signin/apikey'
  body = '{}'
  headers = auth_headers(credentials, nonce=nonce, path=path, body=body)
  headers['Content-Type'] = 'application/json'
  async with HttpClient() as http:
    response = await http.request('POST', base_url + path, content=body, headers=headers)
    if not response.is_success:
      raise_http_status(response)
    return response.json()['accessToken']['token']
