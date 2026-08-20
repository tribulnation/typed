"""Credential resolution and request signing, shared by the HTTP and WS API transports."""

from typing_extensions import Any, Mapping
from dataclasses import dataclass, field
import hashlib
import hmac
import os
import urllib.parse

from typed_core.exceptions import AuthError

from .types import timestamp_millis


@dataclass(frozen=True)
class Credentials:
  """Binance API key and HMAC-SHA256 secret.

  Binance also documents RSA and Ed25519 keys (Ed25519 is even the venue's own
  recommendation), but every credential this client has been given so far is HMAC — only
  that's implemented, so this stays on stdlib `hmac`/`hashlib` rather than adding a
  dependency (`cryptography` or similar) for algorithms nothing here actually uses yet.
  Extending `sign()` to dispatch on a `key_type` is the natural next step if that changes.
  """

  api_key: str
  secret: str = field(repr=False)


def resolve_credentials(
  api_key: str | None, secret: str | None, *, public: bool
) -> Credentials | None:
  """Resolve the one `Credentials` every Binance transport shares.

  Called once, from `Venue.new()` — not from each transport's own construction, so every
  surface signs with the same key.

  Args:
    api_key: Binance API key; read from `BINANCE_API_KEY` when omitted.
    secret: HMAC secret; read from `BINANCE_SECRET_KEY` when omitted.
    public: Skip resolution entirely and return `None`, for a credential-free client.

  Raises:
    AuthError: `public` is false and no credentials were passed or found in the environment.
  """
  if public:
    return None
  api_key = api_key or os.environ.get('BINANCE_API_KEY')
  secret = secret or os.environ.get('BINANCE_SECRET_KEY')
  if not api_key or not secret:
    raise AuthError(
      'No credentials: set BINANCE_API_KEY/BINANCE_SECRET_KEY, pass api_key/secret, '
      'or build with `public=True` for the credential-free surface.'
    )
  return Credentials(api_key, secret)


def sign(payload: str, credentials: Credentials) -> str:
  """Hex-encoded HMAC-SHA256 of `payload`, keyed by `credentials.secret` — case-insensitive
  on Binance's side, unlike RSA/Ed25519 signatures.

  Args:
    payload: The exact bytes signed, ASCII (Binance requires non-ASCII characters
      percent-encoded before signing, which `urllib.parse.urlencode` already does).
    credentials: API key and secret.
  """
  return hmac.new(
    credentials.secret.encode(), payload.encode('ascii'), hashlib.sha256
  ).hexdigest()


def signed_params(
  params: Mapping[str, Any] | None,
  credentials: Credentials,
  *,
  recv_window: int | None = None,
) -> dict[str, Any]:
  """Return `params` plus `timestamp`, optional `recvWindow`, and `signature` — the
  signed-request shape both REST and the WS API build on.

  Params are sorted before signing, and the returned dict preserves that same sorted
  order (`signature` appended last) rather than the caller's original insertion order.
  REST doesn't strictly need sorting — Binance verifies the literal bytes it received,
  whatever order the caller sent them in — but the returned dict's order still has to
  *match* whatever `encoded` here was built from, since `transport/http.py` re-encodes
  this same dict to build the actual request. Returning it unsorted while signing sorted
  bytes was a real bug: any signed call with 2+ business params in non-alphabetical
  declaration order sent bytes that didn't match what was signed, and Binance rejected it
  with `-1022 Invalid signature` — reproduced live with a bare `{symbol, orderId}` call to
  `/api/v3/order`, since every endpoint captured before this had only ever exercised a
  single business param. The WS API sends `params` as a JSON object instead of a literal
  byte string, so this ordering was never load-bearing there — sorting only matters
  because Binance reconstructs a canonical string server-side to verify (confirmed live
  against `userDataStream.subscribe.signature`).

  Args:
    params: Request params to sign alongside; not mutated.
    credentials: API key and secret.
    recv_window: `recvWindow`, milliseconds; omitted entirely when `None`, so Binance's
      own 5000ms default applies.

  Note:
    `apiKey` is deliberately never added here: REST sends it as a header, so it's not
    part of the signed payload there, while the WS API signs it alongside everything
    else. Add it to `params` before calling this when signing a WS API request.
  """
  query = dict(params or {})
  query['timestamp'] = timestamp_millis.now()
  if recv_window is not None:
    query['recvWindow'] = recv_window
  query = dict(sorted(query.items()))
  encoded = urllib.parse.urlencode(query, doseq=True)
  query['signature'] = sign(encoded, credentials)
  return query
