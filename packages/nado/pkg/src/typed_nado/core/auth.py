"""Credentials: the EVM key that signs, and the subaccount it signs for.

Nado has no API keys. Every write is an EIP-712 signature by either the subaccount's owner
wallet or the one signer it has linked (`link_signer`), which then has full permissions. A
bot therefore holds the linked signer's key and names the owner address separately.
"""

from dataclasses import dataclass, field
import os

from eth_account import Account
from eth_account.signers.local import LocalAccount
from eth_utils.address import is_address, to_checksum_address

from .exc import AuthError, BadRequest
from .networks import NetworkProfile

DEFAULT_SUBACCOUNT = 'default'
"""Name of the subaccount the app creates on a wallet's first deposit."""


def subaccount_bytes32(owner: str, name: str) -> str:
  """The `bytes32` hex of a subaccount: its 20-byte owner address followed by its name,
  ASCII, right-padded with zeros to 12 bytes.

  Args:
    owner: Owner wallet address.
    name: Subaccount name, at most 12 ASCII bytes.

  Raises:
    BadRequest: The address or the name is invalid.
  """
  if not is_address(owner):
    raise BadRequest(f'Invalid owner address: {owner!r}')
  try:
    raw = name.encode('ascii')
  except UnicodeEncodeError:
    raise BadRequest(f'Subaccount name must be ASCII: {name!r}') from None
  if len(raw) > 12:
    raise BadRequest(f'Subaccount name longer than 12 bytes: {name!r}')
  return '0x' + bytes.fromhex(owner[2:]).hex() + raw.ljust(12, b'\0').hex()


@dataclass(frozen=True, kw_only=True)
class Credentials:
  """The signing key of one client, and the subaccount it acts for by default."""

  account: LocalAccount = field(repr=False)
  """The signing key: the owner wallet's own, or its linked signer's."""
  owner: str
  """Checksummed address of the wallet owning the subaccount."""
  subaccount: str = DEFAULT_SUBACCOUNT
  """Subaccount name: `default` unless the wallet created others."""

  @property
  def signer(self) -> str:
    """Checksummed address of the signing key."""
    return self.account.address

  @property
  def sender(self) -> str:
    """The default subaccount, as the `bytes32` hex every signed payload's `sender` takes."""
    return subaccount_bytes32(self.owner, self.subaccount)


def resolve_credentials(
  profile: NetworkProfile,
  *,
  private_key: str | None,
  address: str | None,
  subaccount: str | None,
  public: bool,
) -> Credentials | None:
  """Resolve the one `Credentials` every signing transport of a client shares.

  Called once, from the root's `.new()`. A key passed as an argument is never paired with
  an environment variable: `address` then defaults to the key's own address, and
  `subaccount` to `default`. Otherwise all three are read from the environment, under the
  network's prefix (`NADO_` on mainnet, `NADO_TESTNET_` on testnet), and an explicit
  `address` or `subaccount` overrides its variable.

  Args:
    profile: The deployment, which picks the variable prefix.
    private_key: Signing key, hex; read from `{prefix}PRIVATE_KEY` when omitted.
    address: Owner wallet of the subaccount, when the key is a linked signer; read from
      `{prefix}ADDRESS` when the key comes from the environment.
    subaccount: Subaccount name; read from `{prefix}SUBACCOUNT` when the key comes from the
      environment.
    public: Skip resolution entirely and return `None`, for a client that never signs.

  Raises:
    AuthError: `public` is false and no key was passed or found, or the key is invalid.
    BadRequest: The address or the subaccount name is invalid.
  """
  if public:
    return None
  prefix = profile.env_prefix
  if private_key is None:
    private_key = os.environ.get(f'{prefix}PRIVATE_KEY')
    address = address or os.environ.get(f'{prefix}ADDRESS')
    subaccount = subaccount or os.environ.get(f'{prefix}SUBACCOUNT')
  if not private_key:
    raise AuthError(
      f'No Nado signing key: set {prefix}PRIVATE_KEY, pass private_key, or build with '
      '`public=True` for the read-only surface.'
    )
  try:
    account: LocalAccount = Account.from_key(private_key)
  except (ValueError, TypeError):
    raise AuthError('Invalid Nado private key') from None
  owner = address or account.address
  if not is_address(owner):
    raise BadRequest(f'Invalid owner address: {owner!r}')
  subaccount = subaccount or DEFAULT_SUBACCOUNT
  subaccount_bytes32(
    owner, subaccount
  )  # rejects a bad name now, not on the first signed call
  return Credentials(
    account=account, owner=to_checksum_address(owner), subaccount=subaccount
  )
