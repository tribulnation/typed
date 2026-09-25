"""API keys: the `Signer` protocol every signing path goes through, and `PythonSigner`.

A `Signer` is one Lighter API key. Its whole job is lighter-go's own `signer.Signer`
interface: Schnorr-sign a 40-byte message hash. Everything else (validation, hashing,
`tx_info` encoding, auth tokens) is shared Python code on top of it, so another backend (a
compiled one, an HSM, a remote signing service) only has to implement `public_key` and
`sign`, and every transaction type works with it unchanged.
"""

from typing_extensions import Protocol
from dataclasses import dataclass, field
import secrets

from ..exc import AuthError
from . import schnorr
from .curve import N


class Signer(Protocol):
  """One API key: signs 40-byte message hashes (Schnorr over ECgFp5, Poseidon2 challenge)."""

  @property
  def public_key(self) -> bytes:
    """The 40-byte public key registered on the venue for this key's slot."""
    ...

  def sign(self, msg_hash: bytes) -> bytes:
    """The 80-byte signature (s || e, little-endian) of a 40-byte message hash."""
    ...


@dataclass(frozen=True, kw_only=True)
class ApiKeyPair:
  """A freshly generated API key pair, hex-encoded (little-endian)."""

  private_key: str = field(repr=False)
  """Private key, `0x`-prefixed as lighter-go prints it; register its public half with
  `change_api_key` before use."""
  public_key: str
  """Public key, bare lowercase hex exactly as `GET /apikeys` reports it
  (`client.api.account.keys.list`), so the two compare equal."""


def parse_private_key(private_key: str) -> int:
  """The private scalar of a hex API private key (40 bytes little-endian, optional `0x`).

  Like Go's `NewKeyManager`, a value >= n is reduced mod n.

  Raises:
    AuthError: The key is not hex, or not 40 bytes long.
  """
  try:
    raw = bytes.fromhex(private_key.removeprefix('0x'))
  except ValueError:
    raise AuthError('invalid private key: not hex') from None
  if len(raw) != 40:
    raise AuthError(f'invalid private key length. expected: 40 got: {len(raw)}')
  return schnorr.scalar_from_bytes(raw)


@dataclass(frozen=True)
class PythonSigner:
  """`Signer` in pure Python: the default backend.

  Deterministic apart from the hedged nonce (see `schnorr`); no global state, so any number
  of keys, accounts and networks can sign concurrently in one process. Not constant-time
  (see `typed_lighter.core.signer`).

  Examples:
    ```python
    key = PythonSigner.from_hex('0x...')
    signature = key.sign(msg_hash)
    ```
  """

  scalar: int = field(repr=False)
  """The private scalar, in [0, n)."""
  public_key: bytes
  """The 40-byte public key: build with `from_scalar`, `from_hex` or `generate`, which derive it."""

  @classmethod
  def from_scalar(cls, scalar: int) -> 'PythonSigner':
    """Wrap a private scalar (reduced mod n), deriving its public key.

    Args:
      scalar: The private scalar.
    """
    scalar %= N
    return cls(scalar=scalar, public_key=schnorr.public_key(scalar))

  @classmethod
  def from_hex(cls, private_key: str) -> 'PythonSigner':
    """Load a hex API private key, as `GenerateAPIKey`/`create_api_key` print it.

    Args:
      private_key: 40 bytes of hex, `0x` optional.

    Raises:
      AuthError: The key is not 40 bytes of hex.
    """
    return cls.from_scalar(parse_private_key(private_key))

  @classmethod
  def generate(cls) -> 'PythonSigner':
    """A fresh key, uniform in [0, n) from the OS CSPRNG (Go uses `crypto/rand` the same way)."""
    return cls.from_scalar(secrets.randbelow(N))

  def sign(self, msg_hash: bytes) -> bytes:
    """Sign a 40-byte message hash with a hedged nonce.

    Args:
      msg_hash: The 40-byte Poseidon2 hash to sign.
    """
    return schnorr.sign(msg_hash, self.scalar)

  def key_pair(self) -> ApiKeyPair:
    """This key, hex-encoded: the private key `0x`-prefixed, the public key bare, as the venue reports it."""
    return ApiKeyPair(
      private_key='0x' + schnorr.scalar_to_bytes(self.scalar).hex(),
      public_key=self.public_key.hex(),
    )


def generate_api_key() -> ApiKeyPair:
  """Generate a fresh API key pair locally (lighter-go `GenerateAPIKey`)."""
  return PythonSigner.generate().key_pair()
