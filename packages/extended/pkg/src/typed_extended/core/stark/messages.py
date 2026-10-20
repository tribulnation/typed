"""SNIP-12 (revision 1) typed-data hashing of the four structs Extended's settlement
signatures cover: `Order`, `LimitOrder`, `TransferArgs` and `WithdrawArgs`.

A signed message hash is `poseidon(["StarkNet Message", domain_hash, public_key,
struct_hash])`, where each struct hash is `poseidon([type_selector, *fields])` in field
order. The type selectors are `sn_keccak` of each struct's full type string; they are
constants, written out here (the tests recompute them from the type strings).
"""

from dataclasses import dataclass

from .curve import P
from .poseidon import poseidon_hash_many

DOMAIN_SELECTOR = 0x1FF2F602E42168014D405A94F75E8A93D640751D71D16311266E140D8B0A210
"""`sn_keccak('"StarknetDomain"("name":"shortstring","version":"shortstring","chainId":"shortstring","revision":"shortstring")')`."""
ORDER_SELECTOR = 0x36DA8D51815527CABFAA9C982F564C80FA7429616739306036F1F9B608DD112
"""`sn_keccak` of the `Order` type string (with its `PositionId`, `AssetId`, `Timestamp` dependencies)."""
LIMIT_ORDER_SELECTOR = 0x3C79B3B5997E78A29AB2FB5E8BC8244F222C5E01AE914C10F956BD0F805199A
"""`sn_keccak` of the `LimitOrder` type string."""
TRANSFER_SELECTOR = 0x1DB88E2709FDF2C59E651D141C3296A42B209CE770871B40413EA109846A3B4
"""`sn_keccak` of the `TransferArgs` type string."""
WITHDRAW_SELECTOR = 0x250A5FA378E8B771654BD43DCB34844534F9D1E29E16B14760D7936EA7F4B1D
"""`sn_keccak` of the `WithdrawArgs` type string."""


def short_string(value: str) -> int:
  """Encode a Cairo short string (at most 31 ASCII characters) as a field element.

  Raises:
    ValueError: The string is longer than 31 characters or not ASCII.
  """
  data = value.encode('ascii')
  if len(data) > 31:
    raise ValueError(f'Short string too long: {value!r}')
  return int.from_bytes(data, 'big')


MESSAGE_PREFIX = short_string('StarkNet Message')
"""The fixed first element of every SNIP-12 message hash."""


@dataclass(frozen=True, kw_only=True)
class StarknetDomain:
  """The SNIP-12 domain every settlement signature is bound to (`GET /info/starknet`)."""

  name: str = 'Perpetuals'
  """Domain name."""
  version: str = 'v0'
  """Domain version."""
  chain_id: str
  """Starknet chain id: `SN_MAIN` or `SN_SEPOLIA`."""
  revision: int = 1
  """SNIP-12 revision; hashed as the integer, not as a short string."""

  def hash(self) -> int:
    """The domain's struct hash."""
    return poseidon_hash_many(
      [
        DOMAIN_SELECTOR,
        short_string(self.name),
        short_string(self.version),
        short_string(self.chain_id),
        self.revision,
      ]
    )


def message_hash(domain: StarknetDomain, public_key: int, struct_hash: int) -> int:
  """The SNIP-12 message hash of a struct, as signed by `public_key`'s owner."""
  return poseidon_hash_many([MESSAGE_PREFIX, domain.hash(), public_key, struct_hash])


def felt(value: int) -> int:
  """A signed integer as a field element (negative `i64` amounts wrap modulo `P`)."""
  return value % P


@dataclass(frozen=True, kw_only=True)
class Order:
  """An `Order` settlement: every perpetual or spot order, and each TP/SL leg."""

  position_id: int
  """The signer's vault (collateral position)."""
  base_asset_id: int
  """Synthetic asset id (market `l2Config.syntheticId`)."""
  base_amount: int
  """Synthetic amount in quantums: positive to buy, negative to sell."""
  quote_asset_id: int
  """Collateral asset id (market `l2Config.collateralId`)."""
  quote_amount: int
  """Collateral amount in quantums: negative to buy, positive to sell."""
  fee_asset_id: int
  """Fee asset id (the collateral)."""
  fee_amount: int
  """Maximum fee in collateral quantums."""
  expiration: int
  """Settlement expiration, epoch seconds."""
  salt: int
  """The order nonce."""

  def hash(self) -> int:
    """The struct hash."""
    return poseidon_hash_many(
      [
        ORDER_SELECTOR,
        self.position_id,
        self.base_asset_id,
        felt(self.base_amount),
        self.quote_asset_id,
        felt(self.quote_amount),
        self.fee_asset_id,
        self.fee_amount,
        self.expiration,
        self.salt,
      ]
    )


@dataclass(frozen=True, kw_only=True)
class LimitOrder:
  """A `LimitOrder` settlement: vault share deposits and withdrawals."""

  source_position: int
  """Position the order is sent from."""
  receive_position: int
  """Position receiving the proceeds."""
  base_asset_id: int
  """Base asset id."""
  base_amount: int
  """Base amount in quantums (signed)."""
  quote_asset_id: int
  """Quote asset id."""
  quote_amount: int
  """Quote amount in quantums (signed)."""
  fee_asset_id: int
  """Fee asset id."""
  fee_amount: int
  """Maximum fee in quantums."""
  expiration: int
  """Settlement expiration, epoch seconds."""
  salt: int
  """The order nonce."""

  def hash(self) -> int:
    """The struct hash."""
    return poseidon_hash_many(
      [
        LIMIT_ORDER_SELECTOR,
        self.source_position,
        self.receive_position,
        self.base_asset_id,
        felt(self.base_amount),
        self.quote_asset_id,
        felt(self.quote_amount),
        self.fee_asset_id,
        self.fee_amount,
        self.expiration,
        self.salt,
      ]
    )


@dataclass(frozen=True, kw_only=True)
class Transfer:
  """A `TransferArgs` settlement: a transfer between sub-accounts of one wallet."""

  recipient: int
  """Receiving vault."""
  position_id: int
  """Sending vault."""
  collateral_id: int
  """Transferred asset id."""
  amount: int
  """Amount in quantums."""
  expiration: int
  """Settlement expiration, epoch seconds."""
  salt: int
  """The transfer nonce."""

  def hash(self) -> int:
    """The struct hash."""
    return poseidon_hash_many(
      [
        TRANSFER_SELECTOR,
        self.recipient,
        self.position_id,
        self.collateral_id,
        self.amount,
        self.expiration,
        self.salt,
      ]
    )


@dataclass(frozen=True, kw_only=True)
class Withdrawal:
  """A `WithdrawArgs` settlement: a withdrawal to a Starknet address."""

  recipient: int
  """Receiving Starknet contract address."""
  position_id: int
  """Sending vault."""
  collateral_id: int
  """Withdrawn asset id."""
  amount: int
  """Amount in quantums."""
  expiration: int
  """Settlement expiration, epoch seconds."""
  salt: int
  """The withdrawal nonce."""

  def hash(self) -> int:
    """The struct hash."""
    return poseidon_hash_many(
      [
        WITHDRAW_SELECTOR,
        self.recipient,
        self.position_id,
        self.collateral_id,
        self.amount,
        self.expiration,
        self.salt,
      ]
    )


Message = Order | LimitOrder | Transfer | Withdrawal
"""Any struct a settlement signature covers."""
