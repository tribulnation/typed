"""Ed25519 wallets and the signed request envelope, shared by every signed surface
(`exchange`, the signed `user` types, `solana`).

Margin Trade has no API keys: an account *is* a Solana Ed25519 public key. Each signed request
carries `{a, n, u, ts, s, v}`, where `s` signs the RFC 8785 canonical JSON of `{a, n, ts}`, plus
`v` only when it is non-empty (an agent acting for its master account).
"""

from typing_extensions import Any, Mapping, TypedDict
from datetime import datetime
from dataclasses import dataclass, field
import re
import threading

import base58
import rfc8785
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from typed_core.exceptions import AuthError

from .networks import NetworkCode, NetworkProfile
from .types import timestamp_millis

HEX_SEED = re.compile(r'^(0x)?[0-9a-fA-F]{64}$')
"""A 32-byte Ed25519 seed in hex: the format the API docs use."""


def public_address(key: Ed25519PrivateKey) -> str:
  """The base58 address (raw 32-byte public key) of a private key."""
  raw = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
  return base58.b58encode(raw).decode()


class SigningClocks:
  """Request timestamps per signer address, strictly increasing for each address.

  Ed25519 is deterministic, so two identical actions signed in the same millisecond would
  produce byte-identical envelopes, which the venue refuses as `duplicate signature` for
  ~125 s. Each timestamp is `max(now, last + 1)` for the signing address: at most a few ms
  ahead of the clock under a burst, well inside the venue's 60 s of allowed skew.

  Keyed by address rather than held on a `Wallet`, so every wallet (and every client) built
  from the same key in this process shares one sequence; one process-wide instance,
  `signing_clocks`, serves them all. Another process signing with the same key keeps its own
  sequence, so it can still collide within one millisecond.
  """

  def __init__(self):
    """An empty registry: no address has signed yet."""
    self.last: dict[str, int] = {}
    """The last timestamp handed out per address, epoch ms."""
    self.lock = threading.Lock()
    """Guards `last` across threads; asyncio tasks never interleave inside `next`."""

  def next(self, address: str) -> int:
    """The next request timestamp for `address`, epoch ms: now, or one past the last one
    handed out to it if that is later.
    """
    with self.lock:
      ts = max(timestamp_millis.now(), self.last.get(address, 0) + 1)
      self.last[address] = ts
      return ts


signing_clocks = SigningClocks()
"""The process-wide signing clock every wallet draws its request timestamps from."""


@dataclass(frozen=True)
class Wallet:
  """One Ed25519 signing key: a master account's own key, or an approved agent ("API wallet").

  Two wallets are equal (and hash alike) when their public keys are: equality never looks at
  the private key.
  """

  key: Ed25519PrivateKey = field(repr=False, compare=False)
  """The private key. Never printed, never compared."""
  address: str
  """Base58 public key: the account address when this is a master key."""

  @classmethod
  def parse(cls, secret: str | bytes) -> 'Wallet':
    """Load a wallet from any of the formats Margin Trade hands out.

    Args:
      secret: A hex 32-byte seed (the API docs' format, `0x` optional), a base58 64-byte
        Solana secret key (seed + public key, what the web app's API-wallet page shows), a
        base58 32-byte seed, or raw bytes: the 32-byte seed, or the 64-byte seed + public
        key.

    Raises:
      AuthError: `secret` is none of these, or a 64-byte secret's public half does not match
        its seed.
    """
    if isinstance(secret, bytes):
      seed = secret
    elif HEX_SEED.match(secret := secret.strip()):
      seed = bytes.fromhex(secret.removeprefix('0x'))
    else:
      try:
        seed = base58.b58decode(secret)
      except ValueError:
        raise AuthError('Malformed private key: expected hex or base58.') from None
    if len(seed) == 64:
      seed, public = seed[:32], seed[32:]
      wallet = cls.from_seed(seed)
      if base58.b58decode(wallet.address) != public:
        raise AuthError(
          'Malformed private key: its public half does not match its seed.'
        )
      return wallet
    elif len(seed) == 32:
      return cls.from_seed(seed)
    else:
      raise AuthError(
        f'Malformed private key: expected 32 or 64 bytes, got {len(seed)}.'
      )

  @classmethod
  def from_seed(cls, seed: bytes) -> 'Wallet':
    """Build a wallet from a raw 32-byte Ed25519 seed.

    Raises:
      AuthError: `seed` is not 32 bytes long.
    """
    if len(seed) != 32:
      raise AuthError(
        f'Malformed private key: expected a 32-byte seed, got {len(seed)}.'
      )
    key = Ed25519PrivateKey.from_private_bytes(seed)
    return cls(key, public_address(key))

  @classmethod
  def generate(cls) -> 'Wallet':
    """A fresh random keypair (its address is a new, empty account)."""
    key = Ed25519PrivateKey.generate()
    return cls(key, public_address(key))

  def sign(self, message: bytes) -> bytes:
    """The raw 64-byte Ed25519 signature of `message`."""
    return self.key.sign(message)

  def next_ts(self) -> int:
    """The next request timestamp for this key's address (see `SigningClocks`), epoch ms."""
    return signing_clocks.next(self.address)

  def __copy__(self) -> 'Wallet':
    """The wallet itself: it is frozen and its key immutable, so a copy is never needed."""
    return self

  def __deepcopy__(self, memo: dict[int, Any]) -> 'Wallet':
    """The wallet itself, as `__copy__`: nothing in it can change."""
    return self

  def __reduce__(self):
    """Refuse to pickle: a pickle would carry the private seed in the clear.

    Raises:
      TypeError: Always. Pass the key itself across process boundaries deliberately and
        rebuild with `Wallet.from_seed` (or `Wallet.parse`) on the other side.
    """
    raise TypeError(
      'Wallet cannot be pickled: it would write the private key in the clear. Send the key '
      'explicitly and rebuild it with `Wallet.from_seed` (or `Wallet.parse`).'
    )


@dataclass(frozen=True)
class Credentials:
  """The signer every signed surface shares, and the account it acts for."""

  wallet: Wallet
  """The signing key."""
  vault: str | None = None
  """Master account the wallet acts for, when it is an approved agent; `None` when the wallet
  is the master key itself.
  """

  @property
  def account(self) -> str:
    """The account signed requests operate on."""
    return self.vault or self.wallet.address

  @property
  def is_master(self) -> bool:
    """Whether the wallet is the account's own key (not an agent)."""
    return self.vault is None or self.vault == self.wallet.address


def resolve_credentials(
  wallet: Wallet | str | bytes | None, *, vault: str | None, public: bool
) -> Credentials | None:
  """Resolve the one signer a client's signed surfaces share.

  Args:
    wallet: The signing key, or a private key in any format `Wallet.parse` takes.
    vault: Master account address, when `wallet` is an approved agent.
    public: Skip credentials entirely and return `None`, for a client that only reads.

  Raises:
    ValueError: `public` is true and a `wallet` or `vault` was given too (it would be
      ignored).
    AuthError: `public` is false and no wallet was given, or the key is malformed.
  """
  if public:
    if wallet is not None or vault is not None:
      raise ValueError(
        '`public=True` builds a client without a wallet: drop `wallet=`/`vault=`, or '
        '`public=True`.'
      )
  elif wallet is None:
    raise AuthError(
      'No wallet: pass `wallet=` (a private key or `Wallet`), or build with `public=True` '
      'for the read-only surface.'
    )
  else:
    parsed = wallet if isinstance(wallet, Wallet) else Wallet.parse(wallet)
    return Credentials(parsed, vault or None)


class SignedEnvelope(TypedDict):
  """The body of every signed request."""

  a: Mapping[str, Any]
  """The action: `type` plus its parameters."""
  n: NetworkCode
  """Network code: `m` (mainnet) or `t` (testnet)."""
  u: str
  """Signer's base58 public key."""
  ts: int
  """Request time, epoch milliseconds; must be within 60 s of the server's clock."""
  s: str
  """Base58 Ed25519 signature."""
  v: str
  """Master account when signing as an agent; `""` otherwise."""


def signing_message(
  action: Mapping[str, Any], *, network: NetworkCode, ts: int, vault: str
) -> bytes:
  """The exact bytes a signed request signs: RFC 8785 canonical `{a, n, ts}`, plus `v` only
  when it is non-empty.

  Args:
    action: The action payload, `type` included.
    network: Network code (`m`/`t`).
    ts: Request time in epoch ms.
    vault: The master account when signing as an agent, `""` otherwise.

  References:
    - [Authentication](https://docs.margin.trade/api/authentication)
  """
  data: dict[str, Any] = {'a': action, 'n': network, 'ts': ts}
  if vault:
    data['v'] = vault
  return rfc8785.dumps(data)


class AgentConsent(TypedDict):
  """An agent key's co-signed consent to act for a master account (`approveAgentV2`)."""

  signature: str
  """Base58 Ed25519 signature: `agentConsentSignature`."""
  timestamp: datetime
  """When the consent was signed: `agentConsentTimestamp`."""


def agent_consent(
  agent: Wallet,
  *,
  master: str,
  network: NetworkProfile,
  ts: int | None = None,
) -> AgentConsent:
  """Sign an agent key's consent to be approved by `master`, for `exchange.approve_agent_v2`.

  The agent signs the standard signing bytes of a consent action,
  `{"a": {"type": "approveAgentConsent", "masterAddress", "agentAddress"}, "n", "ts"}`
  (RFC 8785, no `v`), with its own key; the master then sends the approval.

  Args:
    agent: The agent key being approved.
    master: The master account address approving it.
    network: The deployment the approval is sent to (`client.network`): its code is signed
      in, so a consent can only be used on that network.
    ts: Consent time in epoch ms; defaults to the agent's next signing timestamp.

  Examples:
    ```python
    consent = agent_consent(agent, master=wallet.address, network=client.network)
    await client.exchange.approve_agent_v2(
      agent_address=agent.address,
      agent_consent_signature=consent['signature'],
      agent_consent_timestamp=consent['timestamp'],
    )
    ```
  """
  ts = agent.next_ts() if ts is None else ts
  action = {
    'type': 'approveAgentConsent',
    'masterAddress': master,
    'agentAddress': agent.address,
  }
  signature = agent.sign(signing_message(action, network=network.code, ts=ts, vault=''))
  return {
    'signature': base58.b58encode(signature).decode(),
    'timestamp': timestamp_millis.parse(ts),
  }


def sign_action(
  action: Mapping[str, Any],
  credentials: Credentials,
  *,
  network: NetworkCode,
  ts: int | None = None,
) -> SignedEnvelope:
  """Sign `action` into a request envelope.

  Args:
    action: The action payload, `type` included.
    credentials: Signer and the account it acts for.
    network: Network code (`m`/`t`).
    ts: Request time in epoch ms; defaults to the signer address's next timestamp (now, or
      one past the last one handed out to that address in this process), so concurrent
      identical calls in this process never produce the same signature, even from two
      clients built from one key.

  References:
    - [Authentication](https://docs.margin.trade/api/authentication)
  """
  ts = credentials.wallet.next_ts() if ts is None else ts
  vault = '' if credentials.is_master else credentials.account
  signature = credentials.wallet.sign(
    signing_message(action, network=network, ts=ts, vault=vault)
  )
  return {
    'a': action,
    'n': network,
    'u': credentials.wallet.address,
    'ts': ts,
    's': base58.b58encode(signature).decode(),
    'v': vault,
  }
