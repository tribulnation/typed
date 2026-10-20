"""Credential resolution: the API key every private call sends, and the optional Stark
account signed calls (orders, transfers, withdrawals) also need.

An API key alone gives read access plus the unsigned writes (cancels, leverage, referral
writes). Creating orders, transferring or withdrawing additionally needs the sub-account's
Stark private key and vault, all shown on the venue's API management page.
"""

from dataclasses import dataclass, field
import os

from .exc import AuthError
from .networks import NetworkProfile
from .stark.backend import BackendName, backend as select_backend
from .stark.settlement import StarkAccount


@dataclass(frozen=True)
class Credentials:
  """What a private call authenticates with."""

  api_key: str = field(repr=False)
  """The sub-account's API key, sent as `X-Api-Key`."""
  stark: StarkAccount | None = None
  """The sub-account's Stark key pair and vault; `None` for a read-only client."""


def parse_int(value: str, *, name: str) -> int:
  """Parse a decimal or `0x`-prefixed hex integer.

  Raises:
    AuthError: The value is not an integer.
  """
  try:
    return int(value, 16) if value.lower().startswith('0x') else int(value)
  except ValueError:
    raise AuthError(f'{name} is not an integer') from None


def resolve_stark_account(
  *,
  private_key: str | None,
  public_key: str | None,
  vault: int | str | None,
  backend: BackendName | None,
  prefix: str,
) -> StarkAccount | None:
  """Build the Stark account from arguments, or `None` when no private key is configured.

  Raises:
    AuthError: A private key is configured without a vault, a value is malformed, or the
      given public key does not match the private key.
  """
  if not private_key:
    return None
  crypto = select_backend(backend)
  key = parse_int(private_key, name=f'{prefix}_STARK_PRIVATE_KEY')
  try:
    derived = crypto.public_key(key)
  except ValueError:
    raise AuthError(
      f'{prefix}_STARK_PRIVATE_KEY is not a valid Stark private key'
    ) from None
  if public_key and parse_int(public_key, name=f'{prefix}_STARK_PUBLIC_KEY') != derived:
    raise AuthError(f'{prefix}_STARK_PUBLIC_KEY does not match the Stark private key')
  if vault is None or vault == '':
    raise AuthError(
      f'A Stark private key needs its vault: set {prefix}_VAULT or pass `vault`.'
    )
  position = (
    vault if isinstance(vault, int) else parse_int(vault, name=f'{prefix}_VAULT')
  )
  return StarkAccount(
    private_key=key, public_key=derived, vault=position, backend=crypto
  )


def resolve_credentials(
  *,
  profile: NetworkProfile,
  public: bool,
  api_key: str | None,
  stark_private_key: str | None,
  stark_public_key: str | None,
  vault: int | str | None,
  backend: BackendName | None = None,
) -> Credentials | None:
  """Resolve the one set of credentials a client's REST and stream transports share, from
  arguments first and `EXTENDED_*` environment variables second (`EXTENDED_TESTNET_*` on
  testnet): `_API_KEY`, `_STARK_PRIVATE_KEY`, `_STARK_PUBLIC_KEY` (optional, checked
  against the private key) and `_VAULT`.

  Args:
    profile: The network, which picks the environment prefix.
    public: Skip credentials entirely: public market data and streams only.
    api_key: API key.
    stark_private_key: Stark private key, hex.
    stark_public_key: Stark public key, hex; derived from the private key when omitted.
    vault: The sub-account's vault (position id).
    backend: Force a Stark crypto backend.

  Raises:
    AuthError: `public` is false and no API key was found, or the Stark settings are
      incomplete or inconsistent.
  """
  if public:
    return None
  prefix = profile.env_prefix
  api_key = api_key or os.environ.get(f'{prefix}_API_KEY')
  if not api_key:
    raise AuthError(
      f'No credentials: set {prefix}_API_KEY (plus {prefix}_STARK_PRIVATE_KEY and '
      f'{prefix}_VAULT for signed calls), pass `api_key`, or build with `public=True`.'
    )
  stark = resolve_stark_account(
    private_key=stark_private_key or os.environ.get(f'{prefix}_STARK_PRIVATE_KEY'),
    public_key=stark_public_key or os.environ.get(f'{prefix}_STARK_PUBLIC_KEY'),
    vault=vault if vault is not None else os.environ.get(f'{prefix}_VAULT'),
    backend=backend,
    prefix=prefix,
  )
  return Credentials(api_key=api_key, stark=stark)
