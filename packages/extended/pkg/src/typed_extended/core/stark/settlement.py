"""Building the `settlement` objects Extended's signed requests carry: amounts converted to
Stark quantums with the venue's rounding rules, hashed as SNIP-12 structs and signed.

Everything here is pure: market and asset parameters, keys, nonces and expirations are
inputs, so the exact bytes the venue receives are reproducible from the vendor's own test
vectors.
"""

from typing_extensions import Literal, TypedDict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR, ROUND_UP, Context, Decimal
import math
import secrets

from .backend import StarkBackend
from .curve import Signature
from .messages import Order, StarknetDomain, Transfer, Withdrawal

Side = Literal['BUY', 'SELL']
"""Order side."""

ORDER_EXPIRATION_BUFFER = timedelta(days=14)
"""Added to an order's `expiryEpochMillis` to get its signed settlement expiration."""
TRANSFER_EXPIRATION = timedelta(days=21)
"""Signed expiration of a transfer, from now."""
WITHDRAWAL_EXPIRATION = timedelta(days=15)
"""Signed expiration of a withdrawal, from now (the venue's minimum is 14 days)."""
MAX_NONCE = 2**31
"""Largest nonce the venue documents."""

BUY_ROUNDING = Context(rounding=ROUND_UP)
SELL_ROUNDING = Context(rounding=ROUND_DOWN)
FEE_ROUNDING = Context(rounding=ROUND_UP)


@dataclass(frozen=True, kw_only=True)
class StarkAccount:
  """The Stark key pair and vault one sub-account signs settlements with."""

  private_key: int
  """Stark private key."""
  public_key: int
  """Stark public key (`l2Key`), derived from the private key when not given."""
  vault: int
  """The sub-account's position id (`l2Vault`)."""
  backend: StarkBackend
  """Crypto implementation used to hash and sign."""

  def __repr__(self) -> str:
    """Never show the private key."""
    return f'StarkAccount(public_key={hex(self.public_key)}, vault={self.vault})'

  def sign(
    self, message: Order | Transfer | Withdrawal, *, domain: StarknetDomain
  ) -> tuple[int, Signature]:
    """Hash a settlement struct for this key and sign it, returning `(msg_hash, signature)`."""
    msg_hash = self.backend.message_hash(
      message, domain=domain, public_key=self.public_key
    )
    return msg_hash, self.backend.sign(self.private_key, msg_hash)


@dataclass(frozen=True, kw_only=True)
class L2Config:
  """A market's Stark settlement parameters (`GET /info/markets` `l2Config`)."""

  synthetic_id: int
  """Synthetic asset id."""
  synthetic_resolution: int
  """Quantums per unit of the synthetic asset."""
  collateral_id: int
  """Collateral asset id."""
  collateral_resolution: int
  """Quantums per unit of collateral."""


class SignatureJson(TypedDict):
  """A signature as the venue takes it: hex `r` and `s`."""

  r: str
  s: str


class OrderSettlementJson(TypedDict):
  """An order's (or TP/SL leg's) `settlement`."""

  signature: SignatureJson
  starkKey: str
  collateralPosition: str


class DebuggingAmountsJson(TypedDict):
  """The signed quantum amounts, sent alongside an order for the venue's diagnostics."""

  collateralAmount: str
  feeAmount: str
  syntheticAmount: str


class TransferSettlementJson(TypedDict):
  """A transfer's `settlement`."""

  amount: int
  assetId: str
  expirationTimestamp: int
  nonce: int
  receiverPositionId: int
  receiverPublicKey: str
  senderPositionId: int
  senderPublicKey: str
  signature: SignatureJson


class ExpirationJson(TypedDict):
  """A settlement expiration."""

  seconds: int


class WithdrawalSettlementJson(TypedDict):
  """A withdrawal's `settlement`."""

  recipient: str
  positionId: int
  collateralId: str
  amount: int
  expiration: ExpirationJson
  salt: int
  signature: SignatureJson


@dataclass(frozen=True, kw_only=True)
class SignedOrder:
  """An order settlement, signed."""

  msg_hash: int
  """The signed message hash; the SDK's default external order id is its decimal string."""
  settlement: OrderSettlementJson
  """The `settlement` object."""
  debugging_amounts: DebuggingAmountsJson
  """The signed quantum amounts."""


def signature_json(signature: Signature) -> SignatureJson:
  """A signature as hex strings."""
  return {'r': hex(signature.r), 's': hex(signature.s)}


def new_nonce() -> int:
  """A random nonce in `[1, 2^31]`, the venue's documented range."""
  return secrets.randbelow(MAX_NONCE) + 1


def to_quantums(
  value: Decimal, resolution: int, rounding: Context | None = None
) -> int:
  """Convert a human amount to integer quantums, rounding per `rounding` (exact-to-even
  when absent, as transfers and withdrawals do)."""
  if rounding is None:
    return int((value * resolution).to_integral_exact())
  return int(
    rounding.multiply(value, Decimal(resolution)).to_integral(context=rounding)
  )


def order_expiration(expiry_millis: int) -> int:
  """The signed settlement expiration of an order: its expiry plus 14 days, in seconds,
  rounded up."""
  return math.ceil(expiry_millis / 1000) + int(ORDER_EXPIRATION_BUFFER.total_seconds())


def expiration_from_now(delta: timedelta, now: datetime | None = None) -> int:
  """`now + delta`, as epoch seconds rounded up."""
  now = now or datetime.now(timezone.utc)
  return math.ceil((now + delta).timestamp())


def entire_position_size(
  *, price: Decimal, min_order_size_change: Decimal, max_position_value: Decimal
) -> Decimal:
  """The size an entire-position TP/SL leg is signed for: large enough that the position
  can never outgrow it by the time the leg executes (`maxPositionValue * 50 / price`)."""
  precision = abs(int(min_order_size_change.log10().to_integral_exact(ROUND_CEILING)))
  quantum = Decimal(10) ** -precision
  return (max_position_value * 50 / price).quantize(quantum, rounding=ROUND_FLOOR)


def sign_order(
  *,
  account: StarkAccount,
  domain: StarknetDomain,
  l2: L2Config,
  side: Side,
  qty: Decimal,
  price: Decimal,
  fee_rate: Decimal,
  nonce: int,
  expiry_millis: int,
) -> SignedOrder:
  """Sign one order (or one TP/SL leg).

  A buy rounds both amounts up and pays collateral (negative collateral amount); a sell
  rounds both down and delivers the synthetic (negative synthetic amount). The fee is
  `fee_rate * qty * price` in collateral, always rounded up.

  Args:
    account: The signing sub-account.
    domain: The network's SNIP-12 domain.
    l2: The market's settlement parameters.
    side: Order side (for a TP/SL leg, the side the leg trades).
    qty: Size in the synthetic asset.
    price: Worst accepted price.
    fee_rate: Total fee rate: the order's `fee` plus any `builderFee`.
    nonce: The order nonce (the struct's `salt`).
    expiry_millis: The order's `expiryEpochMillis`.
  """
  rounding = BUY_ROUNDING if side == 'BUY' else SELL_ROUNDING
  synthetic = to_quantums(qty, l2.synthetic_resolution, rounding)
  collateral = to_quantums(qty * price, l2.collateral_resolution, rounding)
  fee = to_quantums(fee_rate * qty * price, l2.collateral_resolution, FEE_ROUNDING)
  if side == 'BUY':
    collateral = -collateral
  else:
    synthetic = -synthetic
  message = Order(
    position_id=account.vault,
    base_asset_id=l2.synthetic_id,
    base_amount=synthetic,
    quote_asset_id=l2.collateral_id,
    quote_amount=collateral,
    fee_asset_id=l2.collateral_id,
    fee_amount=fee,
    expiration=order_expiration(expiry_millis),
    salt=nonce,
  )
  msg_hash, signature = account.sign(message, domain=domain)
  return SignedOrder(
    msg_hash=msg_hash,
    settlement={
      'signature': signature_json(signature),
      'starkKey': hex(account.public_key),
      'collateralPosition': str(account.vault),
    },
    debugging_amounts={
      'collateralAmount': str(collateral),
      'feeAmount': str(fee),
      'syntheticAmount': str(synthetic),
    },
  )


def sign_transfer(
  *,
  account: StarkAccount,
  domain: StarknetDomain,
  receiver_vault: int,
  receiver_public_key: int,
  asset_id: int,
  resolution: int,
  amount: Decimal,
  nonce: int,
  expiration: int,
) -> TransferSettlementJson:
  """Sign a transfer from `account`'s vault to another sub-account's.

  Args:
    account: The sending sub-account.
    domain: The network's SNIP-12 domain.
    receiver_vault: The receiving sub-account's `l2Vault`.
    receiver_public_key: The receiving sub-account's `l2Key`.
    asset_id: The transferred asset's Stark id (`starkexId`).
    resolution: The asset's quantums per unit.
    amount: Amount in asset units.
    nonce: The transfer nonce.
    expiration: Signed expiration, epoch seconds.
  """
  quantums = to_quantums(amount, resolution)
  message = Transfer(
    recipient=receiver_vault,
    position_id=account.vault,
    collateral_id=asset_id,
    amount=quantums,
    expiration=expiration,
    salt=nonce,
  )
  _, signature = account.sign(message, domain=domain)
  return {
    'amount': quantums,
    'assetId': hex(asset_id),
    'expirationTimestamp': expiration,
    'nonce': nonce,
    'receiverPositionId': receiver_vault,
    'receiverPublicKey': hex(receiver_public_key),
    'senderPositionId': account.vault,
    'senderPublicKey': hex(account.public_key),
    'signature': signature_json(signature),
  }


def sign_withdrawal(
  *,
  account: StarkAccount,
  domain: StarknetDomain,
  recipient: int,
  asset_id: int,
  resolution: int,
  amount: Decimal,
  nonce: int,
  expiration: int,
) -> WithdrawalSettlementJson:
  """Sign a withdrawal from `account`'s vault to a Starknet address.

  Args:
    account: The withdrawing sub-account.
    domain: The network's SNIP-12 domain.
    recipient: Starknet address receiving the funds (the account's `bridgeStarknetAddress`
      for EVM withdrawals).
    asset_id: The withdrawn asset's Stark id (`starkexId`).
    resolution: The asset's quantums per unit.
    amount: Amount in asset units.
    nonce: The withdrawal nonce (the struct's `salt`).
    expiration: Signed expiration, epoch seconds.
  """
  quantums = to_quantums(amount, resolution)
  message = Withdrawal(
    recipient=recipient,
    position_id=account.vault,
    collateral_id=asset_id,
    amount=quantums,
    expiration=expiration,
    salt=nonce,
  )
  _, signature = account.sign(message, domain=domain)
  return {
    'recipient': hex(recipient),
    'positionId': account.vault,
    'collateralId': hex(asset_id),
    'amount': quantums,
    'expiration': {'seconds': expiration},
    'salt': nonce,
    'signature': signature_json(signature),
  }
