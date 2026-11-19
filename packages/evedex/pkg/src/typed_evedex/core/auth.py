"""Credentials, Sign-In with Ethereum, and the cached JWT session.

EVEDEX has three layers of authentication:

1. An API key, sent as `X-API-Key`. It authorizes private Exchange REST calls only: it is
   not accepted by the Auth service or for private WebSocket channels.
2. A JWT session: `GET /auth/nonce`, an EIP-4361 (SIWE) message signed with the wallet
   (`personal_sign`), `POST /auth/user/sign-up`, then `Authorization: Bearer <access>`.
   The access token is short-lived; `POST /auth/refresh` with `Bearer <refresh>` renews
   both tokens.
3. An EIP-712 signature by the wallet in the body of every order create/replace/close,
   TP/SL create and withdraw, on top of 1 or 2 (`signing.py`).

So the wallet key unlocks everything, and an API key alone is a read-only (REST) client.
"""

from typing_extensions import Any, TypedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import asyncio
import base64
import json
import os

from eth_account import Account
from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount
from eth_utils.address import is_address, to_checksum_address

from typed_core.http import HttpClient

from .environments import EnvironmentProfile
from .exc import AuthError, ValidationError
from .wire import dumps, unwrap

SIWE_DOMAIN = 'evedex.com'
SIWE_URI = 'https://evedex.com'
SIWE_STATEMENT = 'Sign in to evedex.com'
"""The SIWE fields the official SDK signs with, on every environment."""

TOKEN_REFRESH_BUFFER = timedelta(seconds=30)
"""Refresh this long before the access token expires."""


@dataclass(frozen=True, kw_only=True)
class Credentials:
  """What one client authenticates with: a wallet key, an API key, or both."""

  account: LocalAccount | None = field(default=None, repr=False)
  """The wallet: signs in (SIWE) and signs actions (EIP-712)."""
  api_key: str | None = field(default=None, repr=False)
  """An `X-API-Key`, for private Exchange REST calls without a session."""

  @property
  def address(self) -> str | None:
    """Checksummed wallet address, if a wallet key was given."""
    return None if self.account is None else self.account.address


def resolve_credentials(
  profile: EnvironmentProfile,
  *,
  private_key: str | None,
  api_key: str | None,
  address: str | None,
  public: bool,
) -> Credentials | None:
  """Resolve the one `Credentials` every transport of a client shares.

  Called once, from the root's `.new()`. Unset arguments are read from the environment
  under the environment's prefix (`EVEDEX_` on prod, `EVEDEX_DEMO_` on demo):
  `{prefix}PRIVATE_KEY`, `{prefix}API_KEY` and `{prefix}ADDRESS`.

  Args:
    profile: The environment, which picks the variable prefix.
    private_key: Wallet private key, hex.
    api_key: API key.
    address: Expected wallet address, checked against the key's own. Smart-account
      wallets are not supported: the key has to be the account's own EOA.
    public: Skip resolution entirely and return `None`, for an unauthenticated client.

  Raises:
    AuthError: `public` is false and neither key was passed or found, the private key is
      invalid, or `address` is invalid or does not match the private key.
  """
  if public:
    return None
  prefix = profile.env_prefix
  private_key = private_key or os.environ.get(f'{prefix}PRIVATE_KEY') or None
  api_key = api_key or os.environ.get(f'{prefix}API_KEY') or None
  address = address or os.environ.get(f'{prefix}ADDRESS') or None
  if private_key is None and api_key is None:
    raise AuthError(
      f'No EVEDEX credentials: set {prefix}PRIVATE_KEY (or {prefix}API_KEY for '
      'read-only REST), pass private_key/api_key, or build with `public=True`.'
    )
  account: LocalAccount | None = None
  if private_key is not None:
    try:
      key: LocalAccount = Account.from_key(private_key)
    except (ValueError, TypeError):
      raise AuthError('Invalid EVEDEX private key') from None
    account = key
    if address is not None:
      if not is_address(address):
        raise AuthError(f'Invalid EVEDEX address: {address!r}')
      if to_checksum_address(address) != key.address:
        raise AuthError(
          f'{prefix}ADDRESS does not match the private key; smart-account wallets are '
          'not supported'
        )
  return Credentials(account=account, api_key=api_key)


def siwe_message(
  *, address: str, chain_id: int, nonce: str, issued_at: datetime
) -> str:
  """The EIP-4361 sign-in message, exactly as the official SDK's `siwe` builds it."""
  issued = issued_at.astimezone(timezone.utc).isoformat(timespec='milliseconds')
  return (
    f'https://{SIWE_DOMAIN} wants you to sign in with your Ethereum account:\n'
    f'{to_checksum_address(address)}\n'
    '\n'
    f'{SIWE_STATEMENT}\n'
    '\n'
    f'URI: {SIWE_URI}\n'
    'Version: 1\n'
    f'Chain ID: {chain_id}\n'
    f'Nonce: {nonce}\n'
    f'Issued At: {issued.replace("+00:00", "Z")}'
  )


class Tokens(TypedDict):
  """The `token` of a sign-in or refresh response."""

  accessToken: str
  refreshToken: str


def token_expiry(token: str) -> datetime | None:
  """The `exp` claim of a JWT, if it has a readable one. Never verifies the token."""
  try:
    payload = token.split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
    return datetime.fromtimestamp(int(claims['exp']), tz=timezone.utc)
  except (IndexError, ValueError, KeyError, TypeError):
    return None


@dataclass(kw_only=True)
class Session:
  """One wallet's JWT session: signs in lazily, refreshes ahead of expiry and on demand.

  Shared by every transport of a client (Exchange, Auth and market-data REST, and the
  WebSocket's private subscriptions), so the wallet signs in once.
  """

  account: LocalAccount = field(repr=False)
  profile: EnvironmentProfile
  http: HttpClient
  tokens: Tokens | None = field(default=None, init=False, repr=False)
  """The current JWT pair; `None` until the first sign-in."""
  expires_at: datetime | None = field(default=None, init=False, repr=False)
  """When the access token expires, from its `exp` claim; `None` if it has none."""
  exchange_id: int | None = field(default=None, init=False)
  """The account's `exchangeId`, which names its private WebSocket channels."""
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  async def post(
    self, path: str, *, json: Any | None = None, bearer: str | None = None
  ) -> Any:
    """`POST` to the Auth service, returning the bare payload."""
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    if bearer is not None:
      headers['Authorization'] = f'Bearer {bearer}'
    response = await self.http.request(
      'POST',
      self.profile.auth_url + path,
      content=None if json is None else dumps(json),
      headers=headers,
    )
    return unwrap(response)

  def store(self, payload: Any):
    """Keep the tokens of a sign-in or refresh response.

    Raises:
      ValidationError: The response carries no `token.accessToken`/`refreshToken`.
    """
    try:
      tokens: Tokens = {
        'accessToken': payload['token']['accessToken'],
        'refreshToken': payload['token']['refreshToken'],
      }
    except (KeyError, TypeError):
      raise ValidationError(f'Unexpected auth response: {payload!r}') from None
    self.tokens = tokens
    self.expires_at = token_expiry(tokens['accessToken'])

  async def sign_in(self):
    """Sign in with Ethereum: fetch a nonce, sign the SIWE message, exchange it for tokens."""
    response = await self.http.request('GET', self.profile.auth_url + '/auth/nonce')
    nonce = unwrap(response)['nonce']
    message = siwe_message(
      address=self.account.address,
      chain_id=self.profile.chain_id,
      nonce=nonce,
      issued_at=datetime.now(timezone.utc),
    )
    signature = self.account.sign_message(encode_defunct(text=message)).signature.hex()
    payload = await self.post(
      '/auth/user/sign-up',
      json={
        'wallet': self.account.address,
        'message': message,
        'nonce': nonce,
        'signature': '0x' + signature.removeprefix('0x'),
      },
    )
    self.store(payload)

  async def refresh(self):
    """Renew both tokens with the refresh token, signing in again if it was rejected."""
    if self.tokens is None:
      return await self.sign_in()
    try:
      payload = await self.post('/auth/refresh', bearer=self.tokens['refreshToken'])
    except AuthError:
      return await self.sign_in()
    self.store(payload)

  def fresh(self) -> bool:
    """Whether the cached access token can be used for the next request."""
    if self.tokens is None:
      return False
    if self.expires_at is None:
      return True
    return datetime.now(timezone.utc) < self.expires_at - TOKEN_REFRESH_BUFFER

  async def access_token(self) -> str:
    """A usable access token, signing in or refreshing first if needed."""
    async with self.lock:
      if not self.fresh():
        await (self.sign_in() if self.tokens is None else self.refresh())
      assert self.tokens is not None
      return self.tokens['accessToken']

  async def rejected(self, token: str) -> str:
    """Handle a `401` on `token`: refresh, unless another caller already has, and return
    the token to retry with."""
    async with self.lock:
      if self.tokens is None or self.tokens['accessToken'] == token:
        await self.refresh()
      assert self.tokens is not None
      return self.tokens['accessToken']

  async def user_exchange_id(self) -> int:
    """The account's `exchangeId` (`GET /api/user/me`), fetched once and cached."""
    if self.exchange_id is None:
      token = await self.access_token()
      response = await self.http.request(
        'GET',
        self.profile.exchange_url + '/api/user/me',
        headers={'Authorization': f'Bearer {token}', 'Accept': 'application/json'},
      )
      self.exchange_id = int(unwrap(response)['exchangeId'])
    return self.exchange_id
