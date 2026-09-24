"""Credentials and Aster's EIP-712 signing schemes, shared by every signed surface.

Aster has no API keys. A request is authorised by an EIP-712 signature from one of two
EVM wallets:

- the **agent** (API wallet, `signer`), approved by the user, which signs every trading
  and query call as `Message{msg}` over the exact query string;
- the **main wallet** (`user`), which signs management calls (agents, builders,
  sub-accounts), Aster Chain transfers and staking, and the withdrawal `Action` itself.

The functions here only build signatures. Which parameters are appended, in which order,
and which wallet signs is decided per endpoint by the transport (see `http.py`).
"""

from typing_extensions import Any, Mapping, Sequence
from dataclasses import dataclass, field
import os
import time

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_account.signers.local import LocalAccount

from typed_core.exceptions import AuthError

Wallet = LocalAccount | str
"""A wallet: an `eth_account` account, or its hex private key."""

ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

MAINNET_CHAIN_ID = 1666
"""EIP-712 `chainId` of agent `Message{msg}` signatures on mainnet (off-chain id)."""
TESTNET_CHAIN_ID = 714
"""EIP-712 `chainId` of agent `Message{msg}` signatures on testnet."""

EIP712_DOMAIN_TYPE = [
  {'name': 'name', 'type': 'string'},
  {'name': 'version', 'type': 'string'},
  {'name': 'chainId', 'type': 'uint256'},
  {'name': 'verifyingContract', 'type': 'address'},
]

WITHDRAW_CHAIN_NAMES: Mapping[int, str] = {1: 'ETH', 56: 'BSC', 42161: 'Arbitrum'}
"""`destination Chain` names of the EVM withdraw `Action`, by withdraw `chainId`."""


def parse_wallet(wallet: Wallet) -> LocalAccount:
  """Turn a hex private key into an account; pass an account through unchanged."""
  if isinstance(wallet, LocalAccount):
    return wallet
  try:
    return Account.from_key(wallet)
  except (ValueError, TypeError) as e:
    raise AuthError('Invalid wallet private key') from e


@dataclass
class Nonces:
  """Microsecond nonces, strictly increasing within one client.

  Aster rejects a nonce it has already seen, or one older than the 100 most recent for
  the same agent, and one outside ±60 s (±10 s on prediction) of server time. Using the
  wall clock, bumped by one whenever two requests land in the same microsecond, meets
  all three.
  """

  last: int = 0

  def next(self) -> int:
    """Return a fresh nonce, in microseconds since the epoch."""
    self.last = max(time.time_ns() // 1000, self.last + 1)
    return self.last


@dataclass(frozen=True)
class Credentials:
  """The wallets one client signs with.

  `agent` signs every ordinary signed call. `main` is only needed for management calls
  and withdrawals, and is checked lazily, when such a call is made.
  """

  user: str
  """The main wallet's address: the Aster account."""
  agent: LocalAccount | None = field(default=None, repr=False)
  """The approved API wallet (`signer`)."""
  main: LocalAccount | None = field(default=None, repr=False)
  """The main wallet itself, for calls it has to sign."""
  nonces: Nonces = field(default_factory=Nonces, compare=False, repr=False)

  def require_agent(self) -> LocalAccount:
    """The agent wallet.

    Raises:
      AuthError: The client was built without an agent.
    """
    if self.agent is None:
      raise AuthError(
        'No agent wallet: pass `signer` or set ASTER_SIGNER_PRIVATE_KEY to sign this call.'
      )
    return self.agent

  def require_main(self) -> LocalAccount:
    """The main wallet.

    Raises:
      AuthError: The client was built without the main wallet key.
    """
    if self.main is None:
      raise AuthError(
        'This call must be signed by the main wallet: pass `main` or set '
        'ASTER_USER_PRIVATE_KEY.'
      )
    return self.main


USER_ENV = 'ASTER_USER'
"""Main wallet address (the Aster account)."""
SIGNER_ENV = 'ASTER_SIGNER'
"""Agent (API wallet) address; optional, checked against `SIGNER_KEY_ENV` when set."""
SIGNER_KEY_ENV = 'ASTER_SIGNER_PRIVATE_KEY'
"""Agent (API wallet) private key."""
MAIN_KEY_ENV = 'ASTER_USER_PRIVATE_KEY'
"""Main wallet private key; optional, only for management calls and withdrawals."""


def resolve_credentials(
  *,
  user: str | None,
  signer: Wallet | None,
  main: Wallet | None,
  public: bool,
) -> Credentials | None:
  """Resolve the one `Credentials` every signed surface of a client shares.

  Called once, from the root client's `.new()`. Arguments win; each missing one is read
  from the environment (`ASTER_USER`, `ASTER_SIGNER_PRIVATE_KEY`,
  `ASTER_USER_PRIVATE_KEY`, and `ASTER_SIGNER` to cross-check the agent address).

  Args:
    user: The main wallet address. Defaults to `main`'s address when `main` is known.
    signer: The agent (API wallet) private key or account.
    main: The main wallet private key or account, for management calls and withdrawals.
    public: Skip resolution entirely and return `None`, for a credential-free client.

  Raises:
    AuthError: Neither an agent nor a main wallet is available, the account address is
      unknown, or the given addresses do not match the given keys.
  """
  if public:
    return None
  user = user or os.environ.get(USER_ENV) or None
  signer = signer or os.environ.get(SIGNER_KEY_ENV) or None
  main = main or os.environ.get(MAIN_KEY_ENV) or None

  main_account = None if main is None else parse_wallet(main)
  agent = None if signer is None else parse_wallet(signer)
  if agent is None and main_account is None:
    raise AuthError(
      f'No credentials: pass `user` and `signer` (the API wallet private key), set '
      f'{USER_ENV}/{SIGNER_KEY_ENV}, or build with `public=True` for the public surface.'
    )
  if agent is not None and (signer_address := os.environ.get(SIGNER_ENV)):
    if signer_address.lower() != agent.address.lower():
      raise AuthError(f'{SIGNER_ENV} is not the address of the agent private key.')
  if main_account is not None:
    if user is None:
      user = main_account.address
    elif user.lower() != main_account.address.lower():
      raise AuthError('`user` is not the address of the main wallet private key.')
  if user is None:
    raise AuthError(
      f'No account: pass `user` (the main wallet address) or set {USER_ENV}.'
    )
  return Credentials(user=user, agent=agent, main=main_account)


def sign_typed_data(
  account: LocalAccount,
  *,
  domain: Mapping[str, Any],
  primary_type: str,
  fields: Sequence[Mapping[str, str]],
  message: Mapping[str, Any],
) -> str:
  """Sign one EIP-712 typed-data payload and return the `0x`-prefixed hex signature."""
  typed_data = {
    'types': {'EIP712Domain': EIP712_DOMAIN_TYPE, primary_type: list(fields)},
    'primaryType': primary_type,
    'domain': dict(domain),
    'message': dict(message),
  }
  signed = account.sign_message(encode_typed_data(full_message=typed_data))
  return '0x' + signed.signature.hex().removeprefix('0x')


def sign_message(account: LocalAccount, msg: str, *, chain_id: int) -> str:
  """Sign `Message{msg}` under the `AsterSignTransaction` domain.

  Args:
    account: The signing wallet (agent, main wallet, or a sub-account).
    msg: The exact query string sent, excluding `signature`.
    chain_id: The domain `chainId`: 1666/714 for ordinary calls, or the request's own
      `signatureChainId` where the endpoint sends one.
  """
  return sign_typed_data(
    account,
    domain={
      'name': 'AsterSignTransaction',
      'version': '1',
      'chainId': chain_id,
      'verifyingContract': ZERO_ADDRESS,
    },
    primary_type='Message',
    fields=[{'name': 'msg', 'type': 'string'}],
    message={'msg': msg},
  )


def typed_field_type(value: Any) -> str:
  """Infer an EIP-712 field type the way Aster's reference signer does."""
  if isinstance(value, bool):
    return 'bool'
  if isinstance(value, int):
    return 'uint256'
  return 'string'


def sign_action(
  account: LocalAccount,
  params: Sequence[tuple[str, Any]],
  *,
  primary_type: str,
  chain_id: int,
) -> str:
  """Sign a management action (`ApproveAgent`, `UpdateBuilder`, ...) with the main wallet.

  Every sent parameter becomes one struct field, in sending order, its name Title-cased
  (`agentName` -> `AgentName`); booleans are `bool`, integers `uint256`, everything else
  `string`.

  Args:
    account: The main wallet.
    params: The signed parameters, in the order they are sent.
    primary_type: The action's struct name.
    chain_id: The request's `signatureChainId`.
  """
  fields = []
  message: dict[str, Any] = {}
  for key, value in params:
    name = key[:1].upper() + key[1:]
    kind = typed_field_type(value)
    fields.append({'name': name, 'type': kind})
    message[name] = value if kind != 'string' else str(value)
  return sign_typed_data(
    account,
    domain={
      'name': 'AsterSignTransaction',
      'version': '1',
      'chainId': chain_id,
      'verifyingContract': ZERO_ADDRESS,
    },
    primary_type=primary_type,
    fields=fields,
    message=message,
  )


def sign_withdraw(
  account: LocalAccount,
  *,
  chain_id: int,
  signature_chain_id: int,
  receiver: str,
  asset: str,
  amount: str,
  fee: str,
  nonce: int,
  mainnet: bool,
) -> str:
  """Sign the EVM withdraw `Action` with the main wallet.

  Args:
    account: The main wallet.
    chain_id: The withdraw chain, which names the `destination Chain`.
    signature_chain_id: The EIP-712 domain `chainId`, normally `chain_id`.
    receiver: The destination address.
    asset: The token name, e.g. `USDT`.
    amount: The amount, in token units.
    fee: The fee, in token units.
    nonce: The `userNonce` sent alongside the signature.
    mainnet: Sign for `Mainnet` rather than `Testnet`.

  Raises:
    ValueError: `chain_id` is not a documented withdraw chain.
  """
  chain_name = WITHDRAW_CHAIN_NAMES.get(chain_id)
  if chain_name is None:
    raise ValueError(f'Unsupported EVM withdraw chainId: {chain_id}')
  return sign_typed_data(
    account,
    domain={
      'name': 'Aster',
      'version': '1',
      'chainId': signature_chain_id,
      'verifyingContract': ZERO_ADDRESS,
    },
    primary_type='Action',
    fields=[
      {'name': 'type', 'type': 'string'},
      {'name': 'destination', 'type': 'address'},
      {'name': 'destination Chain', 'type': 'string'},
      {'name': 'token', 'type': 'string'},
      {'name': 'amount', 'type': 'string'},
      {'name': 'fee', 'type': 'string'},
      {'name': 'nonce', 'type': 'uint256'},
      {'name': 'aster chain', 'type': 'string'},
    ],
    message={
      'type': 'Withdraw',
      'destination': receiver,
      'destination Chain': chain_name,
      'token': asset,
      'amount': amount,
      'fee': fee,
      'nonce': nonce,
      'aster chain': 'Mainnet' if mainnet else 'Testnet',
    },
  )
