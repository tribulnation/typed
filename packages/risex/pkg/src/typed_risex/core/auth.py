"""Credentials and the JWT session.

RISEx has no exchange-issued API keys. A client acts for one **account** (the wallet that
holds collateral) through two EVM keys:

- the **account key**, which signs only setup actions: registering or revoking a signer,
  granting an OperatorHub allowance;
- the **signer key** (a session key registered on-chain against the account), which signs
  every trading permit, the WebSocket `auth_v2` handshake and, on the account's behalf,
  JWT logins.

Either key alone is useful: the account key can register a signer; the signer key can trade
(given the account's address). Calls needing a JWT log in lazily, with whichever key is
available, and refresh the token before it expires.
"""

from typing_extensions import Awaitable, Callable, Literal, TypedDict
from dataclasses import dataclass, field
import asyncio
import os
import time

from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_utils.address import is_address, to_checksum_address

from .exc import AuthError

ACCOUNT_KEY_ENV = 'RISEX_ACCOUNT_KEY'
"""Environment variable holding the account's private key."""
SIGNER_KEY_ENV = 'RISEX_SIGNER_KEY'
"""Environment variable holding the signer (session key) private key."""
ACCOUNT_ENV = 'RISEX_ACCOUNT'
"""Environment variable holding the account's address, for a signer-only setup."""


@dataclass(frozen=True, kw_only=True)
class Credentials:
  """The account a client acts for, and the keys it may sign with."""

  account: str
  """The account's checksummed address."""
  account_key: LocalAccount | None = field(default=None, repr=False)
  """The account's own key: signs setup actions."""
  signer_key: LocalAccount | None = field(default=None, repr=False)
  """The registered signer (session) key: signs permits, logins and WebSocket auth."""
  source: Literal['arguments', 'environment'] = 'arguments'
  """Where the keys came from: `new()`'s arguments, or the environment."""

  @property
  def signer(self) -> str | None:
    """The signer's address, if a signer key is configured."""
    return self.signer_key.address if self.signer_key is not None else None

  def require_account_key(self) -> LocalAccount:
    """The account key, for a setup action.

    Raises:
      AuthError: No account key is configured.
    """
    if self.account_key is None:
      raise AuthError(
        f'This call is signed by the account itself: set {ACCOUNT_KEY_ENV} or pass `account_key`.'
      )
    return self.account_key

  def require_signer_key(self) -> LocalAccount:
    """The signer key, for a permit or WebSocket authentication.

    Raises:
      AuthError: No signer key is configured.
    """
    if self.signer_key is None:
      raise AuthError(
        f'This call is signed by a registered signer: set {SIGNER_KEY_ENV} or pass `signer_key`.'
      )
    return self.signer_key


def load_key(key: str, name: str) -> LocalAccount:
  """Parse a hex private key.

  Raises:
    AuthError: `key` is not a valid private key. The key itself is never echoed.
  """
  try:
    return Account.from_key(key)
  except Exception:
    raise AuthError(f'`{name}` is not a valid hex private key') from None


def resolve_credentials(
  *,
  account_key: str | None = None,
  signer_key: str | None = None,
  account: str | None = None,
  public: bool = False,
) -> Credentials | None:
  """Resolve the one `Credentials` every transport of a client shares.

  Called once, from the root's `.new()`. Keys come from one source only, so an explicit key
  is never paired with another account's key from the environment: if either key is
  passed, the arguments are the whole set; otherwise `RISEX_ACCOUNT_KEY`,
  `RISEX_SIGNER_KEY` and `RISEX_ACCOUNT` are read.

  Args:
    account_key: The account's private key, hex.
    signer_key: The signer's private key, hex.
    account: The account's address; required with a signer key alone, checked against the
      account key otherwise.
    public: Skip resolution and return `None`, for a public-only client.

  Raises:
    AuthError: Neither key was found, the account's address is unknown, or it does not
      match the account key.
  """
  if public:
    return None
  source: Literal['arguments', 'environment'] = 'arguments'
  if not account_key and not signer_key:
    source = 'environment'
    account_key = os.environ.get(ACCOUNT_KEY_ENV) or None
    signer_key = os.environ.get(SIGNER_KEY_ENV) or None
    account = account or os.environ.get(ACCOUNT_ENV) or None
  if not account_key and not signer_key:
    raise AuthError(
      f'No RISEx keys: set {ACCOUNT_KEY_ENV} and/or {SIGNER_KEY_ENV} (with {ACCOUNT_ENV}), '
      'pass account_key/signer_key, or build with `public=True` for public data only.'
    )
  account_acct = load_key(account_key, 'account_key') if account_key else None
  signer_acct = load_key(signer_key, 'signer_key') if signer_key else None
  if account is not None and not is_address(account):
    raise AuthError(f'`account` is not an address: {account!r}')
  if account_acct is not None:
    if account is not None and to_checksum_address(account) != account_acct.address:
      raise AuthError('`account` does not match the address of `account_key`')
    address = account_acct.address
  elif account is not None:
    address = to_checksum_address(account)
  else:
    raise AuthError(
      f'A signer key alone needs the account it trades for: set {ACCOUNT_ENV} or pass `account`.'
    )
  return Credentials(
    account=address, account_key=account_acct, signer_key=signer_acct, source=source
  )


class Tokens(TypedDict):
  """`POST /v1/auth/login` and `POST /v1/auth/refresh` payload."""

  access_token: str
  refresh_token: str
  expires_in: int
  """Access token lifetime, in seconds."""
  token_type: str


REFRESH_BEFORE = 60
"""Seconds before the access token expires at which the session refreshes it."""


@dataclass
class Session:
  """One lazily opened JWT session: logs in on first use, refreshes ahead of expiry
  (the refresh token rotates on every refresh), and logs in again if refreshing fails.
  """

  tokens: Tokens | None = field(default=None, repr=False)
  expires_at: float = 0
  """Unix seconds at which the access token expires."""
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  async def token(
    self,
    login: Callable[[], Awaitable[Tokens]],
    refresh: Callable[[str], Awaitable[Tokens]],
  ) -> str:
    """A live access token.

    Args:
      login: Performs a fresh EIP-712 login.
      refresh: Exchanges a refresh token for new tokens.
    """
    async with self.lock:
      now = time.time()
      if self.tokens is not None and now < self.expires_at - REFRESH_BEFORE:
        return self.tokens['access_token']
      tokens = None
      if self.tokens is not None:
        try:
          tokens = await refresh(self.tokens['refresh_token'])
        except AuthError:
          tokens = None
      if tokens is None:
        tokens = await login()
      self.tokens, self.expires_at = tokens, now + tokens['expires_in']
      return tokens['access_token']

  def invalidate(self):
    """Drop the tokens, so the next call logs in again (after a `401`, say)."""
    self.tokens = None
    self.expires_at = 0
