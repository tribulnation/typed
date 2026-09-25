"""Credential resolution and auth tokens, shared by the REST and WebSocket transports.

Lighter has three credential layers: the L1
wallet (only for a few L1-signed transactions), API keys (L2 signing keys, one per
`(account_index, api_key_index)`), and auth tokens for private reads, token-gated writes and
private streams. A token is either derived locally from an API key (`DerivedTokens`) or a
server-issued read-only `ro:` token (`StaticToken`); both implement `TokenProvider`.
"""

from typing_extensions import Literal, Mapping, Protocol
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import os

from .exc import AuthError
from .signer.account import AccountSigner
from .signer.key import Signer

TokenScope = Literal['read', 'write']
"""What a token can authorize: `read` for private reads, `write` also for token-gated writes."""


class TokenProvider(Protocol):
  """Supplies the auth token attached to private REST calls and private WS subscriptions."""

  @property
  def account_index(self) -> int:
    """Account the token authenticates."""
    ...

  @property
  def scope(self) -> TokenScope:
    """Whether the token can authorize token-gated writes, or private reads only."""
    ...

  def token(self) -> str:
    """A currently valid token."""
    ...


@dataclass(kw_only=True)
class DerivedTokens:
  """Standard auth tokens, signed locally from an API key and cached until shortly before expiry.

  Signing is local and synchronous, so a token is never fetched over the network and there
  is nothing to lock against concurrent refresh.
  """

  signer: AccountSigner
  """Signer holding the API key the tokens are derived from."""
  lifetime: timedelta = timedelta(minutes=10)
  """Lifetime of each new token (at most 8 hours)."""
  refresh_before: timedelta = timedelta(minutes=1)
  """Sign a new token this long before the cached one expires."""
  cached: tuple[str, datetime] | None = field(default=None, init=False, repr=False)
  """The last signed token and its expiry, reused until `refresh_before` it."""

  @property
  def account_index(self) -> int:
    """Account the tokens authenticate."""
    return self.signer.account_index

  @property
  def scope(self) -> TokenScope:
    """Derived tokens authorize token-gated writes too."""
    return 'write'

  def token(self) -> str:
    """The cached token, or a freshly signed one when it is about to expire."""
    now = datetime.now(timezone.utc)
    if self.cached is None or now >= self.cached[1] - self.refresh_before:
      expires_at = now + self.lifetime
      self.cached = (self.signer.auth_token(expires_at=expires_at), expires_at)
    return self.cached[0]


@dataclass(frozen=True, kw_only=True)
class StaticToken:
  """A fixed token: a server-issued read-only `ro:` token, or a pre-signed standard one."""

  value: str = field(repr=False)
  """The token itself."""
  account_index: int
  """Account the token authenticates, read from the token."""
  scope: TokenScope = 'read'
  """`read` for a read-only `ro:` token, `write` for a standard one."""

  @classmethod
  def parse(cls, value: str) -> 'StaticToken':
    """Wrap a token, reading its account index from the token itself.

    Args:
      value: A `ro:{account}:{single|all}:{expiry}:{hex}` read-only token, or a
        `{deadline}:{account}:{key}:{signature}` standard token.

    Raises:
      AuthError: The token has neither shape.
    """
    parts = value.split(':')
    try:
      if parts[0] == 'ro':
        return cls(value=value, account_index=int(parts[1]), scope='read')
      return cls(value=value, account_index=int(parts[1]), scope='write')
    except (IndexError, ValueError):
      raise AuthError('Unrecognized Lighter auth token format') from None

  def token(self) -> str:
    """The fixed token."""
    return self.value


@dataclass(frozen=True)
class Credentials:
  """Everything `Lighter.new()` resolved: at most one signer, and the token source."""

  signer: AccountSigner | None
  """Signs transactions and derives tokens; `None` for public or read-only clients."""
  tokens: TokenProvider | None
  """Token source for private reads; `None` for a public client."""


def env_int(name: str) -> int | None:
  """An integer environment variable, or `None` when unset.

  Raises:
    AuthError: The variable is set but not an integer.
  """
  value = os.environ.get(name)
  if value is None or value == '':
    return None
  try:
    return int(value)
  except ValueError:
    raise AuthError(f'{name} must be an integer') from None


def resolve_api_keys(
  api_keys: Mapping[int, str | Signer] | None,
  api_key_index: int | None,
  api_private_key: str | None,
  *,
  prefix: str,
) -> dict[int, str | Signer] | None:
  """Resolve the API keys, from arguments first and `{prefix}_API_KEY_INDEX`/
  `{prefix}_API_PRIVATE_KEY` second. Returns `None` when none are configured.

  Args:
    api_keys: API keys by slot index: hex private keys, or `Signer`s.
    api_key_index: Slot of a single API key.
    api_private_key: Private key of that single API key.
    prefix: The network's environment variable prefix (`LIGHTER`, `LIGHTER_TESTNET`, ...).

  Raises:
    AuthError: Only one of an API key's index and private key was given.
  """
  if api_keys:
    return dict(api_keys)
  index_var, key_var = f'{prefix}_API_KEY_INDEX', f'{prefix}_API_PRIVATE_KEY'
  index = api_key_index if api_key_index is not None else env_int(index_var)
  private_key = api_private_key or os.environ.get(key_var)
  if index is None and not private_key:
    return None
  if index is None or not private_key:
    raise AuthError(
      'An API key needs both its index and its private key '
      f'({index_var}/{key_var}, or `api_keys={{index: key}}`).'
    )
  return {index: private_key}
