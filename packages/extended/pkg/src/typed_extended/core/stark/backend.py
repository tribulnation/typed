"""Stark crypto backends: the pure-Python implementation in this package, and an optional
native one over the vendor's `fast-stark-crypto` wheel, picked automatically when importable.

Both produce identical results (the tests check them against each other and against the
vendor's test vectors); the native one is only faster, roughly 10x per signature.
"""

from typing_extensions import Literal, Protocol
from dataclasses import dataclass
from functools import lru_cache
from importlib import import_module
from types import ModuleType

from . import curve
from .curve import Signature
from .messages import (
  LimitOrder,
  Message,
  Order,
  StarknetDomain,
  Transfer,
  Withdrawal,
  message_hash,
)

BackendName = Literal['python', 'fast-stark-crypto']
"""A backend: `python` (this package, no dependencies) or `fast-stark-crypto` (native)."""


class StarkBackend(Protocol):
  """Key derivation, SNIP-12 message hashing and signing over the Stark curve."""

  @property
  def name(self) -> BackendName:
    """Which implementation this is."""
    ...

  def public_key(self, private_key: int) -> int:
    """The public key (`x` coordinate) of a private key."""
    ...

  def message_hash(
    self, message: Message, *, domain: StarknetDomain, public_key: int
  ) -> int:
    """The SNIP-12 message hash of a settlement struct, as signed by `public_key`'s owner."""
    ...

  def sign(self, private_key: int, msg_hash: int) -> Signature:
    """Sign a message hash deterministically (RFC 6979)."""
    ...


@dataclass(frozen=True)
class PythonBackend:
  """The pure-Python backend: stdlib only, runs everywhere."""

  name: BackendName = 'python'

  def public_key(self, private_key: int) -> int:
    """The public key (`x` coordinate) of a private key."""
    return curve.public_key(private_key)

  def message_hash(
    self, message: Message, *, domain: StarknetDomain, public_key: int
  ) -> int:
    """The SNIP-12 message hash of a settlement struct."""
    return message_hash(domain, public_key, message.hash())

  def sign(self, private_key: int, msg_hash: int) -> Signature:
    """Sign a message hash deterministically (RFC 6979)."""
    return curve.sign(private_key, msg_hash)


@dataclass(frozen=True)
class FastStarkCryptoBackend:
  """The native backend, over the vendor's `fast-stark-crypto` (Rust, `starknet-crypto`)."""

  module: ModuleType
  """The imported `fast_stark_crypto` module."""
  name: BackendName = 'fast-stark-crypto'

  def public_key(self, private_key: int) -> int:
    """The public key (`x` coordinate) of a private key."""
    return self.module.get_public_key(private_key)

  def message_hash(
    self, message: Message, *, domain: StarknetDomain, public_key: int
  ) -> int:
    """The SNIP-12 message hash of a settlement struct."""
    common = {
      'user_public_key': public_key,
      'domain_name': domain.name,
      'domain_version': domain.version,
      'domain_chain_id': domain.chain_id,
      'domain_revision': str(domain.revision),
    }
    if isinstance(message, Order):
      return self.module.get_order_msg_hash(
        position_id=message.position_id,
        base_asset_id=message.base_asset_id,
        base_amount=message.base_amount,
        quote_asset_id=message.quote_asset_id,
        quote_amount=message.quote_amount,
        fee_asset_id=message.fee_asset_id,
        fee_amount=message.fee_amount,
        expiration=message.expiration,
        salt=message.salt,
        **common,
      )
    if isinstance(message, LimitOrder):
      return self.module.get_limit_order_msg_hash(
        source_position_id=message.source_position,
        receive_position_id=message.receive_position,
        base_asset_id=message.base_asset_id,
        base_amount=message.base_amount,
        quote_asset_id=message.quote_asset_id,
        quote_amount=message.quote_amount,
        fee_asset_id=message.fee_asset_id,
        fee_amount=message.fee_amount,
        expiration=message.expiration,
        salt=message.salt,
        **common,
      )
    if isinstance(message, Transfer):
      return self.module.get_transfer_msg_hash(
        recipient_position_id=message.recipient,
        sender_position_id=message.position_id,
        collateral_id=message.collateral_id,
        amount=message.amount,
        expiration=message.expiration,
        salt=message.salt,
        **common,
      )
    return self.module.get_withdrawal_msg_hash(
      recipient_hex=hex(message.recipient),
      position_id=message.position_id,
      collateral_id=message.collateral_id,
      amount=message.amount,
      expiration=message.expiration,
      salt=message.salt,
      **common,
    )

  def sign(self, private_key: int, msg_hash: int) -> Signature:
    """Sign a message hash deterministically (RFC 6979)."""
    r, s = self.module.sign(private_key=private_key, msg_hash=msg_hash)
    return Signature(r, s)


@lru_cache(maxsize=None)
def fast_backend() -> FastStarkCryptoBackend | None:
  """The native backend, or `None` when `fast-stark-crypto` is not installed."""
  try:
    return FastStarkCryptoBackend(import_module('fast_stark_crypto'))
  except ImportError:
    return None


def backend(name: BackendName | None = None) -> StarkBackend:
  """Pick a backend: the named one, or the native one when installed, else pure Python.

  Args:
    name: Force one backend.

  Raises:
    ImportError: `fast-stark-crypto` was asked for but is not installed.
  """
  if name == 'python':
    return PythonBackend()
  fast = fast_backend()
  if fast is not None:
    return fast
  if name == 'fast-stark-crypto':
    raise ImportError(
      'fast-stark-crypto is not installed: pip install "typed-extended[fast]"'
    )
  return PythonBackend()
