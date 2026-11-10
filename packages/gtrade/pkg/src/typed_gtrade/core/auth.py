"""Trading API authentication: credential resolution, the agent's EIP-712 request
signature, and the typed data a trader's master wallet signs to manage agents and keys.

Two credentials exist, and either may be absent:

- The **agent** key signs every private request (four `X-Gains-*` headers) and the
  WebSocket `auth` frame. The agent is the trader's on-chain trading delegate; it cannot
  move funds.
- A read-only **API key** (`X-Gains-Api-Key`, or `{"op": "auth", "apiKey": ...}` on the
  WebSocket) authorizes private reads only.

The trader's master wallet never reaches the client: registering or revoking an agent
and issuing an API key carry its signature in the request body, over the typed data
`agent_authorization`, `agent_revocation` and `api_key_issue` build (re-exported publicly
from `typed_gtrade.signing`). They take exactly the values the matching endpoints take,
and encode them with the converters the request body uses, so the signed values and the
values sent cannot disagree.

References:
  - [Authentication](https://docs.gains.trade/developer/trading-api/authentication)
"""

from typing_extensions import Any, Literal, TypedDict
from dataclasses import dataclass, field
from datetime import datetime
import os
import time

from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_utils.crypto import keccak

from typed_core.decimals import PlainDecimal, plain

from .chains import (
  REQUEST_DOMAIN_NAME,
  REQUEST_DOMAIN_VERSION,
  Chain,
  Deployment,
  deployment_of,
)
from .exc import AuthError
from .types import TimestampMillis, timestamp_millis

AGENT_KEY_ENV = 'GTRADE_AGENT_PRIVATE_KEY'
"""Environment variable holding the agent's private key (hex)."""
API_KEY_ENV = 'GTRADE_API_KEY'
"""Environment variable holding a read-only Trading API key."""

Wallet = str | LocalAccount
"""A private key (hex string) or an `eth_account` local account."""

EIP712_DOMAIN_FIELDS = [
  {'name': 'name', 'type': 'string'},
  {'name': 'version', 'type': 'string'},
  {'name': 'chainId', 'type': 'uint256'},
  {'name': 'verifyingContract', 'type': 'address'},
]

REQUEST_FIELDS = [
  {'name': 'method', 'type': 'string'},
  {'name': 'path', 'type': 'string'},
  {'name': 'bodyHash', 'type': 'bytes32'},
  {'name': 'timestamp', 'type': 'uint256'},
  {'name': 'nonce', 'type': 'uint256'},
]
"""The signed request struct. Its type name is the operation's OpenAPI `operationId`, so
the same fields are declared under a different primary type per operation."""

AGENT_AUTHORIZATION_FIELDS = [
  {'name': 'agent', 'type': 'address'},
  {'name': 'name', 'type': 'string'},
  {'name': 'markets', 'type': 'string'},
  {'name': 'maxLeverage', 'type': 'string'},
  {'name': 'dailySpendCapUsd', 'type': 'string'},
  {'name': 'expiresAt', 'type': 'uint256'},
  {'name': 'permissions', 'type': 'string'},
  {'name': 'timestamp', 'type': 'uint256'},
]
AGENT_REVOCATION_FIELDS = [
  {'name': 'agent', 'type': 'address'},
  {'name': 'timestamp', 'type': 'uint256'},
]
API_KEY_ISSUE_FIELDS = [
  {'name': 'label', 'type': 'string'},
  {'name': 'timestamp', 'type': 'uint256'},
]

WS_AUTH_OPERATION = 'wsAuth'
"""Primary type of the WebSocket `auth` signature."""
WS_AUTH_METHOD = 'WS'
"""`method` of the WebSocket `auth` signature."""


def body_hash(body: bytes) -> bytes:
  """`keccak256` of the exact request body bytes; an empty body hashes the empty string."""
  return keccak(body)


EMPTY_BODY_HASH = body_hash(b'')
"""`0xc5d2...a470`, the `bodyHash` of a request without a body."""


@dataclass(frozen=True, kw_only=True)
class SigningDomain:
  """The EIP-712 domain of one deployment: every Trading API signature is bound to it."""

  chain_id: int
  verifying_contract: str
  """The deployment's Diamond."""

  @classmethod
  def of(cls, deployment: Deployment) -> 'SigningDomain':
    """The signing domain a deployment pins."""
    return cls(chain_id=deployment.chain_id, verifying_contract=deployment.diamond)

  @classmethod
  def for_chain(cls, chain: Chain) -> 'SigningDomain':
    """The signing domain of a chain's deployment, for signing without a client (a client
    exposes its own as `client.trading.signing_domain`).

    Raises:
      ValueError: `chain` is not a known deployment.
    """
    return cls.of(deployment_of(chain))

  def eip712(self) -> dict[str, Any]:
    """The domain as EIP-712 typed data spells it."""
    return {
      'name': REQUEST_DOMAIN_NAME,
      'version': REQUEST_DOMAIN_VERSION,
      'chainId': self.chain_id,
      'verifyingContract': self.verifying_contract,
    }


def typed_data(
  domain: SigningDomain,
  *,
  primary_type: str,
  fields: list[dict[str, str]],
  message: dict[str, Any],
) -> dict[str, Any]:
  """A complete EIP-712 typed-data document, as `eth_account`'s `full_message` takes it."""
  return {
    'types': {'EIP712Domain': EIP712_DOMAIN_FIELDS, primary_type: fields},
    'primaryType': primary_type,
    'domain': domain.eip712(),
    'message': message,
  }


def request_typed_data(
  domain: SigningDomain,
  *,
  operation: str,
  method: str,
  path: str,
  body: bytes,
  timestamp: int,
  nonce: int,
) -> dict[str, Any]:
  """The typed data the Trading API verifies for one request.

  Args:
    domain: The deployment's signing domain.
    operation: The OpenAPI `operationId` (`createOrder`, `getAccount`, ...), used as the
      primary type.
    method: The HTTP verb, uppercase (`WS` for the WebSocket handshake).
    path: The path with its query string, exactly as sent, starting with `/v1`.
    body: The exact body bytes sent; empty for a request without a body.
    timestamp: Unix milliseconds, within 30 seconds of server time.
    nonce: Never reused by this agent inside the replay window.
  """
  return typed_data(
    domain,
    primary_type=operation,
    fields=REQUEST_FIELDS,
    message={
      'method': method,
      'path': path,
      'bodyHash': body_hash(body),
      'timestamp': timestamp,
      'nonce': nonce,
    },
  )


def sign_typed_data(account: LocalAccount, data: dict[str, Any]) -> str:
  """Sign a typed-data document; returns the 65-byte signature as `0x`-prefixed hex."""
  return account.sign_typed_data(full_message=data).signature.to_0x_hex()


def parse_wallet(wallet: Wallet) -> LocalAccount:
  """An `eth_account` account from a private key or an existing account.

  Raises:
    AuthError: `wallet` is not a valid private key. The key itself is never echoed.
  """
  if isinstance(wallet, LocalAccount):
    return wallet
  try:
    return Account.from_key(wallet)
  except (ValueError, TypeError):
    raise AuthError('Invalid agent private key') from None


@dataclass(frozen=True, kw_only=True)
class SignedRequest:
  """One request's signature and the values signed with it."""

  agent: str
  timestamp: int
  nonce: int
  signature: str

  def headers(self) -> dict[str, str]:
    """The four headers a signed HTTP request carries."""
    return {
      'X-Gains-Agent': self.agent,
      'X-Gains-Timestamp': str(self.timestamp),
      'X-Gains-Nonce': str(self.nonce),
      'X-Gains-Signature': self.signature,
    }


@dataclass(kw_only=True)
class AgentSigner:
  """Signs Trading API requests with an agent key, for one deployment.

  Nonces are `timestamp * 1000`, bumped by one when that would not exceed the last one
  issued, as the official SDK does. One signer must back every transport of a client
  (HTTP and WebSocket), so the two can never issue the same nonce.
  """

  account: LocalAccount = field(repr=False)
  domain: SigningDomain
  last_nonce: int = field(default=0, init=False, repr=False)

  @property
  def address(self) -> str:
    """The agent address, sent as `X-Gains-Agent`."""
    return self.account.address

  def next_nonce(self, timestamp: int) -> int:
    """The next nonce, strictly greater than every nonce issued before."""
    candidate = timestamp * 1000
    self.last_nonce = max(candidate, self.last_nonce + 1)
    return self.last_nonce

  def sign(
    self,
    *,
    operation: str,
    method: str,
    path: str,
    body: bytes = b'',
    timestamp: int | None = None,
  ) -> SignedRequest:
    """Sign one request.

    Args:
      operation: The OpenAPI `operationId`, the primary type.
      method: The HTTP verb, uppercase.
      path: The path with its query string, exactly as sent.
      body: The exact body bytes sent.
      timestamp: Unix milliseconds; now when omitted.
    """
    timestamp = int(time.time() * 1000) if timestamp is None else timestamp
    nonce = self.next_nonce(timestamp)
    data = request_typed_data(
      self.domain,
      operation=operation,
      method=method,
      path=path,
      body=body,
      timestamp=timestamp,
      nonce=nonce,
    )
    return SignedRequest(
      agent=self.address,
      timestamp=timestamp,
      nonce=nonce,
      signature=sign_typed_data(self.account, data),
    )

  def ws_auth(self, path: str) -> dict[str, str]:
    """The WebSocket `auth` frame: the request struct with primary type `wsAuth`, method
    `WS` and an empty body, its timestamp and nonce sent as strings.

    Args:
      path: The WebSocket path, `/v1/{chain}/ws`.
    """
    signed = self.sign(operation=WS_AUTH_OPERATION, method=WS_AUTH_METHOD, path=path)
    return {
      'op': 'auth',
      'agent': signed.agent,
      'timestamp': str(signed.timestamp),
      'nonce': str(signed.nonce),
      'signature': signed.signature,
    }


@dataclass(frozen=True, kw_only=True)
class Credentials:
  """What a client authenticates with: an agent key, a read-only API key, or both."""

  agent: LocalAccount | None = field(default=None, repr=False)
  api_key: str | None = field(default=None, repr=False)


def resolve_credentials(
  *, agent: Wallet | None, api_key: str | None, public: bool
) -> Credentials | None:
  """Resolve a client's credentials, once, from its root `.new()`.

  Explicit arguments win over the environment as a unit: passing either credential reads
  neither variable, so an explicit agent is never paired with an API key of another
  trader's left in the environment. An empty string counts as not passed.

  Args:
    agent: The agent private key or account. When neither credential is passed, read
      from `GTRADE_AGENT_PRIVATE_KEY`.
    api_key: A read-only API key. When neither credential is passed, read from
      `GTRADE_API_KEY`.
    public: Return `None`, for a credential-free client; the environment is not read.

  Raises:
    ValueError: `public` is true and a credential was passed too.
    AuthError: `public` is false and neither credential was passed or found in the
      environment, or the agent key is invalid.
  """
  agent = agent or None
  api_key = api_key or None
  explicit = agent is not None or api_key is not None
  if public:
    if explicit:
      raise ValueError(
        '`public=True` builds a credential-free client: drop `agent`/`api_key`, or '
        'drop `public` to use them.'
      )
    return None
  if not explicit:
    agent = os.environ.get(AGENT_KEY_ENV) or None
    api_key = os.environ.get(API_KEY_ENV) or None
  if agent is None and api_key is None:
    raise AuthError(
      f'No credentials: pass `agent` and/or `api_key`, set {AGENT_KEY_ENV} and/or '
      f'{API_KEY_ENV}, or build with `public=True` for public data only.'
    )
  return Credentials(
    agent=None if agent is None else parse_wallet(agent), api_key=api_key
  )


class AgentScope(TypedDict):
  """An agent's off-chain scope, as `POST /agents` sends it and the master wallet signs it.

  The same shape as the generated `typed_gtrade.trading.schemas.AgentScope` (field for
  field, so either is accepted wherever the other is expected): an agent's scope read
  back from `trading.agents.get` passes straight to `agent_authorization`.
  """

  markets: Literal['all'] | list[str]
  """Symbols the agent may trade (`BTC/USD`), or `all`."""
  maxLeverage: PlainDecimal | None
  """Highest leverage the agent may open or change to; `None` for no limit."""
  dailySpendCapUsd: PlainDecimal | None
  """Rolling UTC-day cap on opened notional, in USD; `None` for no cap."""
  expiresAt: TimestampMillis | None
  """When the agent expires; `None` for no expiry."""
  permissions: Literal['trade', 'read']
  """`read` agents sign private reads and WebSocket auth only."""


def agent_authorization(
  domain: SigningDomain,
  *,
  agent: str,
  name: str | None,
  scope: AgentScope,
  timestamp: datetime,
) -> dict[str, Any]:
  """The `AgentAuthorization` typed data the master wallet signs to register an agent.

  Pass the same `agent`, `name`, `scope` and `timestamp` to `trading.agents.create`. Each
  value is encoded as the request body encodes it (decimals in plain notation, times as
  epoch milliseconds), then as the venue's signed struct spells it: markets comma-joined
  (`*` for `all`), a missing name or limit as the empty string, no expiry as `0`.

  Args:
    domain: The deployment's signing domain (`client.trading.signing_domain`).
    agent: The agent address.
    name: The agent's label; `None` when the request sends none.
    scope: The agent's scope.
    timestamp: When the authorization is signed; the API accepts it within its replay
      window.
  """
  markets = scope['markets']
  max_leverage = scope['maxLeverage']
  spend_cap = scope['dailySpendCapUsd']
  expires_at = scope['expiresAt']
  return typed_data(
    domain,
    primary_type='AgentAuthorization',
    fields=AGENT_AUTHORIZATION_FIELDS,
    message={
      'agent': agent,
      'name': name or '',
      'markets': '*' if markets == 'all' else ','.join(markets),
      'maxLeverage': '' if max_leverage is None else plain(max_leverage),
      'dailySpendCapUsd': '' if spend_cap is None else plain(spend_cap),
      'expiresAt': 0 if expires_at is None else timestamp_millis.dump(expires_at),
      'permissions': scope['permissions'],
      'timestamp': timestamp_millis.dump(timestamp),
    },
  )


def agent_revocation(
  domain: SigningDomain, *, agent: str, timestamp: datetime
) -> dict[str, Any]:
  """The `AgentRevocation` typed data the master wallet signs to revoke an agent.

  Pass the same `agent` and `timestamp` to `trading.agents.revoke`.

  Args:
    domain: The deployment's signing domain (`client.trading.signing_domain`).
    agent: The agent address.
    timestamp: When the revocation is signed, sent as epoch milliseconds.
  """
  return typed_data(
    domain,
    primary_type='AgentRevocation',
    fields=AGENT_REVOCATION_FIELDS,
    message={'agent': agent, 'timestamp': timestamp_millis.dump(timestamp)},
  )


def api_key_issue(
  domain: SigningDomain, *, label: str, timestamp: datetime
) -> dict[str, Any]:
  """The `ApiKeyIssue` typed data the master wallet signs to issue a read-only API key.

  Pass the same `label` and `timestamp` to `trading.api_keys.issue`.

  Args:
    domain: The deployment's signing domain (`client.trading.signing_domain`).
    label: The key's label.
    timestamp: When the issuance is signed, sent as epoch milliseconds.
  """
  return typed_data(
    domain,
    primary_type='ApiKeyIssue',
    fields=API_KEY_ISSUE_FIELDS,
    message={'label': label, 'timestamp': timestamp_millis.dump(timestamp)},
  )
