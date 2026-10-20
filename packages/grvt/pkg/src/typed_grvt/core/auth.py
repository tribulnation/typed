"""Credential resolution and the GRVT session: cookie login, shared by every authenticated transport.

GRVT authenticates calls with a session, not per-request signatures:

1. `POST {edge}/auth/api_key/login` with `{"api_key"}` (or `POST {edge}/auth/wallet/login`
   with an EIP-712 `WalletLogin` signature, for a funding wallet without an API key).
2. The reply sets a `gravity` cookie (24 h `Max-Age` on testnet) and an `X-Grvt-Account-Id`
   header; the body names the funding account and, for a trading-account key, its
   sub-account.
3. Every authenticated call sends `Cookie: gravity=...` and `X-Grvt-Account-Id: ...`.

Payload signatures (orders, transfers, withdrawals) are separate: see `signing.py`.
"""

from dataclasses import dataclass, field
from datetime import timedelta
from http.cookies import CookieError, SimpleCookie
from email.utils import parsedate_to_datetime
import os
import re
import time

import httpx
from typing_extensions import Any, Literal

from typed_core.exceptions import AuthError, ValidationError
from typed_core.http import HttpClient

from .env import Environment
from .envelope import check_edge
from .locks import LoopLock
from .owners import Connection, Owned
from .signing import Signer

ENV_PREFIXES: dict[Environment, str] = {
  'prod': 'GRVT_',
  'testnet': 'GRVT_TESTNET_',
  'staging': 'GRVT_STAGING_',
}
"""Environment-variable prefix per environment, so a testnet credential can never be read
for production: `GRVT_TESTNET_API_KEY`, `GRVT_TESTNET_PRIVATE_KEY`,
`GRVT_TESTNET_TRADING_ACCOUNT_ID` (and `GRVT_API_KEY`, ... for `prod`, the default). The
last is the default trading sub-account: see `GatewayTransport.sub_account_id()`."""

REFRESH_BEFORE = timedelta(minutes=1)
"""Log in again this long before the session cookie expires."""

SESSION_COOKIE = 'gravity'
ACCOUNT_HEADER = 'X-Grvt-Account-Id'


@dataclass(frozen=True, kw_only=True)
class Credentials:
  """GRVT credentials. Either secret alone can open a session; the private key also signs."""

  api_key: str | None = field(default=None, repr=False)
  """API key, exchanged for a session cookie at login."""
  private_key: str | None = field(default=None, repr=False)
  """EIP-712 signer key: the API key's signer, or the funding wallet itself."""
  trading_account_id: str | None = None
  """Default trading sub-account id, filled into a trading call that leaves its
  `sub_account_id` out (see `GatewayTransport.sub_account_id()`)."""
  source: Literal['arguments', 'environment'] = 'arguments'
  """Where the secrets came from: `new()`'s arguments, or the environment variables."""


def resolve_credentials(
  env: Environment,
  *,
  api_key: str | None = None,
  private_key: str | None = None,
  trading_account_id: str | None = None,
  public: bool = False,
) -> Credentials | None:
  """Resolve the one `Credentials` every authenticated transport of a client shares.

  Called once, from the root's `.new()`. The secrets come from one source only, so an
  explicit key is never paired with another account's key from the environment:

  - If `api_key` or `private_key` is passed, the arguments are the whole credential set and
    nothing is read from the environment (`trading_account_id` then defaults to the
    sub-account the API key is scoped to, when not passed).
  - Otherwise all three are read from the environment, under the environment-specific
    prefix (`ENV_PREFIXES`), and an explicit `trading_account_id` overrides
    `{prefix}TRADING_ACCOUNT_ID`.

  Args:
    env: Target environment, which picks the variable prefix.
    api_key: API key; read from `{prefix}API_KEY` when neither secret is passed.
    private_key: Signer private key; read from `{prefix}PRIVATE_KEY` when neither secret is
      passed.
    trading_account_id: Default trading sub-account id; read from
      `{prefix}TRADING_ACCOUNT_ID` when not passed and neither secret is passed.
    public: Skip resolution and return `None`, for a market-data-only client.

  Raises:
    AuthError: `public` is false and neither an API key nor a private key was found.
  """
  if public:
    return None
  prefix = ENV_PREFIXES[env]
  source: Literal['arguments', 'environment'] = 'arguments'
  if not api_key and not private_key:
    source = 'environment'
    api_key = os.environ.get(f'{prefix}API_KEY')
    private_key = os.environ.get(f'{prefix}PRIVATE_KEY')
    trading_account_id = trading_account_id or os.environ.get(
      f'{prefix}TRADING_ACCOUNT_ID'
    )
  if not api_key and not private_key:
    raise AuthError(
      f'No GRVT credentials: set {prefix}API_KEY (and {prefix}PRIVATE_KEY to sign orders, '
      'transfers and withdrawals), pass api_key/private_key, or build with `public=True` '
      'for market data only.'
    )
  return Credentials(
    api_key=api_key,
    private_key=private_key,
    trading_account_id=trading_account_id,
    source=source,
  )


@dataclass(frozen=True, kw_only=True)
class SessionState:
  """One logged-in session."""

  token: str = field(repr=False)
  """`gravity` cookie value."""
  account_id: str | None = field(repr=False)
  """`X-Grvt-Account-Id` header value (an off-chain `ACC:...` id)."""
  expires_at: float
  """Unix seconds at which the cookie expires."""
  funding_account_address: str | None
  """Funding (main) account address the session belongs to."""
  sub_account_id: str | None
  """Trading sub-account id, for a trading-account-level API key."""

  @property
  def headers(self) -> dict[str, str]:
    """Headers authenticating one call with this session."""
    headers = {'Cookie': f'{SESSION_COOKIE}={self.token}'}
    if self.account_id:
      headers[ACCOUNT_HEADER] = self.account_id
    return headers

  def fresh(self) -> bool:
    """Whether the cookie is valid for at least `REFRESH_BEFORE` more."""
    return time.time() < self.expires_at - REFRESH_BEFORE.total_seconds()


MAX_AGE = re.compile(r'-?[0-9]+')
"""A valid cookie `Max-Age`: an integer number of seconds (RFC 6265 §5.2.2)."""


def cookie_expiry(response: httpx.Response) -> float:
  """Unix seconds at which the response's `gravity` cookie expires.

  Reads `Max-Age` first, then `Expires`. An attribute that does not parse is ignored, as
  RFC 6265 has a browser do: a malformed `Max-Age` falls back to `Expires`.

  Raises:
    ValidationError: The response set no `gravity` cookie, or one with no valid lifetime.
  """
  for header in response.headers.get_list('set-cookie'):
    cookie = SimpleCookie()
    try:
      cookie.load(header)
    except CookieError:
      continue
    if (morsel := cookie.get(SESSION_COOKIE)) is None:
      continue
    max_age = morsel['max-age'].strip()
    if MAX_AGE.fullmatch(max_age):
      return time.time() + int(max_age)
    if morsel['expires']:
      try:
        return parsedate_to_datetime(morsel['expires']).timestamp()
      except (TypeError, ValueError, OverflowError):
        pass
  raise ValidationError('Login response set no gravity cookie with a valid lifetime')


def login_failure(payload: Any) -> AuthError:
  """The error for a login the edge host answered without success (an HTTP `200` whose body
  says `"status": "failure"`, or one that is not an object).

  Carries `(code, message, body)` when the body names a venue code, else one message.

  Args:
    payload: The decoded login reply.
  """
  if not isinstance(payload, dict):
    return AuthError(f'Login failed: unexpected reply {payload!r:.500}')
  message = str(
    payload.get('message') or payload.get('error') or payload.get('status') or ''
  )
  if (code := payload.get('code')) is not None:
    return AuthError(code, message, payload)
  return AuthError(f'Login failed: {message or "no reason given"}')


@dataclass(kw_only=True)
class Session(Owned):
  """Lazily logs in, caches the session and refreshes it ahead of expiry.

  Shared by every authenticated transport of one client (trading HTTP, trading WebSocket,
  edge), so a single login serves all of them. Concurrent callers wait on one login; the
  lock is per event loop (`LoopLock`), so a client survives being reused across two
  `asyncio.run` calls, provided each one enters it with `async with client`: leaving it
  closes the HTTP clients and sockets, whose pooled connections otherwise stay bound to the
  first loop and fail in the next one with a raw `RuntimeError`.

  Each transport sharing the session takes one ownership of it while it is owned itself
  (`Owned.shared`), and the login connection closes when the last owner leaves: `async with
  client.trading` alone closes it on exit, while an edge block still open keeps it.
  """

  edge_url: str
  """Edge host base URL, where the login endpoints live."""
  api_key: str | None = field(default=None, repr=False)
  """API key to log in with; preferred over `signer`."""
  signer: Signer | None = None
  """Funding-wallet signer to log in with when there is no API key."""
  http: HttpClient = field(default_factory=HttpClient)
  """Dedicated client, so the login's `Set-Cookie` never lands in a shared cookie jar."""
  current: SessionState | None = field(default=None, init=False, repr=False)
  lock: LoopLock = field(default_factory=LoopLock, init=False, repr=False)

  def connections(self) -> list[Connection]:
    """The login connection, closed when the last owner leaves."""
    return [self.http]

  async def state(self) -> SessionState:
    """The live session, logging in first when there is none or it is about to expire."""
    async with self.lock:
      if self.current is None or not self.current.fresh():
        self.current = await self.login()
      return self.current

  async def headers(self) -> dict[str, str]:
    """Headers authenticating one call."""
    return (await self.state()).headers

  def invalidate(self, state: SessionState):
    """Forget `state` after the venue rejected it, unless a newer session already replaced it.

    Args:
      state: The session the rejected call was sent with.
    """
    if self.current is state:
      self.current = None

  async def login(self) -> SessionState:
    """Log in with the API key, or with a wallet signature when there is no API key.

    Raises:
      AuthError: The venue rejected the credentials, or there are none to log in with.
    """
    if self.api_key:
      path, body = '/auth/api_key/login', {'api_key': self.api_key}
    elif self.signer is not None:
      signature = self.signer.wallet_login()
      path, body = (
        '/auth/wallet/login',
        {'address': self.signer.address, 'signature': signature},
      )
    else:
      raise AuthError('No API key or wallet key to log in with')
    response = await self.http.request('POST', self.edge_url + path, json=body)
    payload = check_edge(response)
    if not isinstance(payload, dict) or payload.get('status', 'success') != 'success':
      raise login_failure(payload)
    token = response.cookies.get(SESSION_COOKIE)
    if not token:
      raise ValidationError('Login response set no gravity cookie')
    return SessionState(
      token=token,
      account_id=response.headers.get(ACCOUNT_HEADER),
      expires_at=cookie_expiry(response),
      funding_account_address=payload.get('funding_account_address'),
      sub_account_id=payload.get('sub_account_id'),
    )
