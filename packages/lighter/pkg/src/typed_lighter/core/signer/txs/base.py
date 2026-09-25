"""What every Lighter L2 transaction shares: limits, Go's error messages, `L2TxAttributes`,
Go-identical JSON, and the validate -> hash -> sign -> encode flow.

Ported from lighter-go v1.0.10 `types/txtypes/{constants,errors,tx_attributes,utils}.go` and
`types/tx_request.go`. Every rule and message below is Go's; a divergence from Go is a bug.

Values reach the hash exactly as Go's `GoldilocksField(x)` casts them: two's complement for a
negative integer (`field.from_go_int`), then reduced mod p.
"""

from typing_extensions import (
  Any,
  ClassVar,
  Literal,
  NoReturn,
  Protocol,
  Required,
  TypedDict,
)
from dataclasses import dataclass, field, fields
import base64
import json

from ...exc import BadRequest, LogicError
from ..field import MASK64, Fp5, from_go_int, to_bytes
from .. import schnorr
from ..poseidon2 import hash_to_fp5

# ---------------------------------------------------------------- limits (constants.go)

MIN_ACCOUNT_INDEX = -1
MAX_ACCOUNT_INDEX = (1 << 48) - 2
MAX_MASTER_ACCOUNT_INDEX = (1 << 47) - 1
MIN_SUB_ACCOUNT_INDEX = 1 << 47
MAX_API_KEY_INDEX = 254
NIL_API_KEY_INDEX = MAX_API_KEY_INDEX + 1
MAX_MARKET_INDEX = (1 << 15) - 1
NIL_MARKET_INDEX = 255
MIN_ASSET_INDEX = 1
MAX_ASSET_INDEX = (1 << 6) - 2
FEE_TICK = 1_000_000
MARGIN_FRACTION_TICK = 10_000
SHARE_TICK = 10_000
ONE_USDC = 1_000_000
ONE_LIT = 100_000_000
INITIAL_POOL_SHARE_VALUE = 1_000
MIN_INITIAL_TOTAL_SHARES = 1_000 * (ONE_USDC // INITIAL_POOL_SHARE_VALUE)
MAX_INITIAL_TOTAL_SHARES = 1_000_000_000 * (ONE_USDC // INITIAL_POOL_SHARE_VALUE)
MIN_POOL_SHARES_TO_MINT_OR_BURN = 1
MAX_POOL_SHARES_TO_MINT_OR_BURN = (1 << 60) - 1
MIN_STAKING_SHARES_TO_MINT_OR_BURN = 1
MAX_STAKING_SHARES_TO_MINT_OR_BURN = (1 << 60) - 1
NB_ATTRIBUTES_PER_TX = 4
MAX_CLIENT_ORDER_INDEX = (1 << 48) - 1
MIN_ORDER_INDEX = MAX_CLIENT_ORDER_INDEX + 1
MAX_ORDER_INDEX = (1 << 60) - 1
MAX_ORDER_BASE_AMOUNT = (1 << 48) - 1
MAX_ORDER_PRICE = (1 << 32) - 1
MAX_ORDER_EXPIRY = (1 << 63) - 1
MAX_GROUPED_ORDER_COUNT = 3
MAX_TIMESTAMP = (1 << 48) - 1
MAX_EXCHANGE_USDC = (1 << 60) - 1
MAX_TRANSFER_AMOUNT = MAX_EXCHANGE_USDC
MAX_WITHDRAWAL_AMOUNT = MAX_EXCHANGE_USDC

# ---------------------------------------------------------------- errors (errors.go)

ERR_ACCOUNT_INDEX_TOO_LOW = f'AccountIndex should not be less than {MIN_ACCOUNT_INDEX}'
ERR_ACCOUNT_INDEX_TOO_HIGH = (
  f'AccountIndex should not be larger than {MAX_ACCOUNT_INDEX}'
)
ERR_FROM_ACCOUNT_INDEX_TOO_LOW = (
  f'FromAccountIndex should not be less than {MIN_ACCOUNT_INDEX}'
)
ERR_FROM_ACCOUNT_INDEX_TOO_HIGH = (
  f'FromAccountIndex should not be larger than {MAX_ACCOUNT_INDEX}'
)
ERR_TO_ACCOUNT_INDEX_TOO_LOW = (
  f'ToAccountIndex should not be less than {MIN_ACCOUNT_INDEX}'
)
ERR_TO_ACCOUNT_INDEX_TOO_HIGH = (
  f'ToAccountIndex should not be larger than {MAX_ACCOUNT_INDEX}'
)
ERR_API_KEY_INDEX_TOO_HIGH = (
  f'ApiKeyIndex should not be larger than {MAX_API_KEY_INDEX}'
)
ERR_NONCE_TOO_LOW = 'AccountNonce should not be less than 0'
ERR_EXPIRED_AT_INVALID = 'ExpiredAt is invalid'
ERR_INVALID_MARKET_INDEX = 'MarketIndex is not valid'
ERR_ASSET_INDEX_TOO_LOW = f'AssetIndex should not be less than {MIN_ASSET_INDEX}'
ERR_ASSET_INDEX_TOO_HIGH = f'AssetIndex should not be larger than {MAX_ASSET_INDEX}'
ERR_ROUTE_TYPE_INVALID = 'RouteType is invalid'
ERR_PUBLIC_POOL_INDEX_TOO_LOW = (
  f'PublicPoolIndex should not be less than {MIN_ACCOUNT_INDEX}'
)
ERR_PUBLIC_POOL_INDEX_TOO_HIGH = (
  f'PublicPoolIndex should not be larger than {MAX_ACCOUNT_INDEX}'
)
ERR_PRICE_TOO_LOW = 'OrderPrice should not be less than 1'
ERR_PRICE_TOO_HIGH = f'OrderPrice should not be larger than {MAX_ORDER_PRICE}'
ERR_TRIGGER_PRICE_INVALID = 'TriggerPrice is invalid'

ATTRIBUTE_ERRORS = {
  1: 'IntegratorAccountIndex is in invalid range',
  2: 'Integrator fees are in invalid range',
  3: 'Integrator fees are in invalid range',
  4: 'Nonce skip attribute is invalid',
  5: 'Cancel all for market index attribute is in invalid range',
  6: 'SelfTradeBehaviorMode is in invalid range',
  7: 'SelfTradeEqualityMode is in invalid range',
  8: 'OrderOrderVersion is in invalid range',
}


def fail(message: str) -> NoReturn:
  """Reject a transaction the way Go's `Validate()` does, with Go's exact message."""
  raise BadRequest(message)


# ---------------------------------------------------------------- Go integer types

GoType = Literal['int16', 'int64', 'uint8', 'uint16', 'uint32', 'uint64']
"""The Go integer type of a transaction field."""

GO_RANGES: dict[GoType, tuple[int, int]] = {
  'int16': (-(1 << 15), (1 << 15) - 1),
  'int64': (-(1 << 63), (1 << 63) - 1),
  'uint8': (0, (1 << 8) - 1),
  'uint16': (0, (1 << 16) - 1),
  'uint32': (0, (1 << 32) - 1),
  'uint64': (0, (1 << 64) - 1),
}


def check_go_int(name: str, value: Any, go_type: GoType):
  """Reject a value its Go field could not hold (Go would silently truncate it instead).

  Go can never produce this error: its fields are already typed, so the message is this
  package's own. The order prices are the exception (see `check_int`).
  """
  lo, hi = GO_RANGES[go_type]
  if not isinstance(value, int) or isinstance(value, bool) or not lo <= value <= hi:
    fail(f'{name} does not fit {go_type}: {value!r}')


def check_int(name: str, value: Any):
  """Reject a non-integer for a field whose range Go's own rules check (the order prices).

  Go stores `Price`/`TriggerPrice` as `uint32`, so its `Price > MaxOrderPrice` check
  (MaxOrderPrice = 2^32 - 1) can never fire there. Here a price is an unbounded `int`, and
  that same check, run in Go's order with Go's message, is what keeps it from truncating.
  """
  if not isinstance(value, int) or isinstance(value, bool):
    fail(f'{name} is not an integer: {value!r}')


# ---------------------------------------------------------------- attributes


@dataclass(frozen=True, kw_only=True)
class Attributes:
  """Optional per-transaction attributes (Go `L2TxAttributes`).

  `None` means "not set", and is omitted from the transaction. A field set explicitly to its
  nil value (integrator fee `0`, cancel-all market `255`, ...) still appears in `tx_info`'s
  `L2TxAttributes`, but is skipped by the hash: Go does the same.
  """

  integrator_account_index: int | None = None
  """Integrator account collecting fees (type 1; nil value 0)."""
  integrator_taker_fee: int | None = None
  """Integrator taker fee in 1e-6 units, at most 1_000_000 (type 2; nil value 0)."""
  integrator_maker_fee: int | None = None
  """Integrator maker fee in 1e-6 units, at most 1_000_000 (type 3; nil value 0)."""
  skip_nonce: int | None = None
  """`1`: accept any increasing nonce (type 4; nil value 0; `0` itself is invalid)."""
  cancel_all_market_index: int | None = None
  """Restrict a cancel-all to one market (type 5; nil value 255)."""
  self_trade_behavior_mode: int | None = None
  """0 expire maker, 1 expire taker, 2 cancel both, 3 reduce (type 6; nil value 0)."""
  self_trade_equality_mode: int | None = None
  """0 same account, 1 same master account (type 7; nil value 0)."""
  order_version: int | None = None
  """Expected order version of a modify (type 8; nil value 0)."""

  GO_TYPES: ClassVar[tuple[GoType, ...]] = (
    'int64',
    'uint32',
    'uint32',
    'uint8',
    'int16',
    'uint8',
    'uint8',
    'int64',
  )
  """Go type of each attribute, in type order (`types.L2TxAttributes`)."""
  RANGES: ClassVar[dict[int, tuple[int, int, int]]] = {
    1: (0, MAX_ACCOUNT_INDEX, 0),
    2: (0, FEE_TICK, 0),
    3: (0, FEE_TICK, 0),
    4: (1, 1, 0),
    5: (0, MAX_MARKET_INDEX, NIL_MARKET_INDEX),
    6: (0, 3, 0),
    7: (0, 1, 0),
    8: (0, MAX_TIMESTAMP, 0),
  }
  """Attribute type -> (min, max, nil value) (`AttributeTypeToConfig`)."""

  def as_map(self) -> dict[int, int]:
    """Go `ConstructL2TxAttributes`: attribute type -> value, for every attribute that is set."""
    values = [getattr(self, f.name) for f in fields(self)]
    return {i + 1: v for i, v in enumerate(values) if v is not None}

  def check_types(self):
    """Reject values the Go attribute field could not hold."""
    for f, go_type in zip(fields(self), self.GO_TYPES):
      value = getattr(self, f.name)
      if value is not None:
        check_go_int(f.name, value, go_type)

  def validate(self):
    """Go `L2TxAttributes.Validate`.

    Go iterates a map, so with several out-of-range attributes it reports a random one of
    their errors; this reports the lowest attribute type's.
    """
    attrs = self.as_map()
    if not attrs:
      return
    if len(attrs) > NB_ATTRIBUTES_PER_TX:
      fail(f'Too many attributes, should not be larger than {NB_ATTRIBUTES_PER_TX}')
    for typ in sorted(attrs):
      lo, hi, _ = self.RANGES[typ]
      if not lo <= attrs[typ] <= hi:
        fail(ATTRIBUTE_ERRORS[typ])
    is_nil = {t: attrs.get(t, nil) == nil for t, (_, _, nil) in self.RANGES.items()}
    has_fees = not is_nil[2] or not is_nil[3]
    if has_fees and is_nil[1]:
      fail(
        'IntegratorAccountIndex should be non-zero when integrator taker fee or maker fee is non-zero'
      )
    if (not is_nil[6] or not is_nil[7]) and has_fees:
      fail("Self-trade specification isn't allowed with integrator fees")
    if attrs.get(6, 0) == 3 and attrs.get(7, 0) == 1:
      fail(
        "Reduce self-trade behavior mode isn't allowed with master account index equality mode"
      )

  def aggregate(self, tx_hash: Fp5) -> bytes:
    """Go `L2TxAttributes.AggregateTxHash`: fold the non-nil attributes into the tx hash.

    Attribute types are sorted ascending and zero-padded to 4 `(type, value)` pairs, hashed,
    and hashed again together with the tx hash. No non-nil attribute: the tx hash as is.
    """
    attrs = self.as_map()
    present = sorted(t for t, v in attrs.items() if v != self.RANGES[t][2])
    if not present:
      return to_bytes(tx_hash)
    elems: list[int] = []
    for t in present + [0] * (NB_ATTRIBUTES_PER_TX - len(present)):
      elems += [t, from_go_int(attrs[t]) if t else 0]
    return to_bytes(hash_to_fp5([*tx_hash, *hash_to_fp5(elems)]))

  def to_json(self) -> dict[str, int] | None:
    """Go's JSON for the attribute map: `null` when nothing is set, keys as sorted strings."""
    attrs = self.as_map()
    if not attrs:
      return None
    return {str(k): attrs[k] for k in sorted(attrs, key=str)}


NO_ATTRIBUTES = Attributes()


# ---------------------------------------------------------------- JSON and L1 messages


def go_json(obj: dict[str, Any]) -> str:
  """Compact JSON the way Go's `encoding/json` marshals these structs (declaration order, no spaces)."""
  return json.dumps(obj, separators=(',', ':'))


def b64(data: bytes) -> str:
  """Go's JSON encoding of a `[]byte` field: standard padded base64."""
  return base64.b64encode(data).decode()


def hex10(value: int) -> str:
  """Go `getHex10FromUint64(uint64(value))`: `0x` plus 16 lowercase hex digits, two's complement."""
  return f'0x{value & MASK64:016x}'


# ---------------------------------------------------------------- signing


class MessageSigner(Protocol):
  """Anything that Schnorr-signs a 40-byte message hash (the `Signer` protocol's core)."""

  def sign(self, msg_hash: bytes) -> bytes:
    """The 80-byte signature of a 40-byte message hash."""
    ...


class TxInfo(TypedDict, total=False):
  """A signed transaction body, decoded from `tx_info`: the fields every type shares. Each
  type also carries its own Go-named fields (`MarketIndex`, `Amount`, ...), which this does
  not list."""

  AccountIndex: int
  """Signing account (every type but transfers and withdrawals)."""
  FromAccountIndex: int
  """Signing account of a transfer or withdrawal."""
  ApiKeyIndex: Required[int]
  """API key slot that signed."""
  ExpiredAt: Required[int]
  """Epoch milliseconds after which the sequencer rejects the transaction."""
  Nonce: Required[int]
  """The API key's nonce."""
  Sig: Required[str]
  """The L2 signature, base64."""
  L1Sig: str
  """The L1 signature, for the types that carry one."""
  L2TxAttributes: dict[str, int] | None
  """Optional attributes by type id, `null` when none is set."""


@dataclass(frozen=True, kw_only=True)
class SignedTx:
  """One signed L2 transaction, ready for `sendTx` (HTTP) or `jsonapi/sendtx` (WS)."""

  tx_type: int
  """Lighter transaction type id (`14` create order, `15` cancel order, ...)."""
  tx_info: str = field(repr=False)
  """The signed transaction body, as the JSON string `sendTx` expects."""
  tx_hash: str
  """The transaction hash, known before submission and equal to the one the venue reports."""
  message_to_sign: str | None = field(default=None, repr=False)
  """The EIP-191 message an Ethereum L1 signature covers, for the three tx types that can
  carry one (`ChangePubKey`, `Transfer`, `ApproveIntegrator`), else `None`."""

  def tx_info_object(self) -> TxInfo:
    """The signed transaction body decoded to a JSON object, as WS `jsonapi/sendtx` expects."""
    return json.loads(self.tx_info)


@dataclass(frozen=True, kw_only=True)
class L2Tx:
  """Fields every user L2 transaction carries, and the flow that signs one.

  A subclass declares `TX_TYPE`, `GO_FIELDS` (its own fields' Go names and types, in Go
  declaration order), and implements `check`, `body_elements` (the hashed fields after the
  common prefix) and `body_json` (its own JSON fields).
  """

  account_index: int
  """Signing account (`AccountIndex`, or `FromAccountIndex` for transfers and withdrawals)."""
  api_key_index: int
  """API key slot that signs."""
  expired_at: int
  """Epoch milliseconds after which the sequencer rejects the transaction."""
  nonce: int
  """The API key's nonce."""
  attributes: Attributes = NO_ATTRIBUTES
  """Optional attributes (`L2TxAttributes`)."""

  TX_TYPE: ClassVar[int]
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = ()
  """(python name, Go name, Go type) of the subclass's own integer fields."""
  ACCOUNT_KEY: ClassVar[str] = 'AccountIndex'
  """JSON key of `account_index`."""

  def check_types(self):
    """Reject values a Go field could not hold, before any of Go's own rules run."""
    check_go_int(self.ACCOUNT_KEY, self.account_index, 'int64')
    check_go_int('ApiKeyIndex', self.api_key_index, 'uint8')
    check_go_int('ExpiredAt', self.expired_at, 'int64')
    check_go_int('Nonce', self.nonce, 'int64')
    for name, go_name, go_type in self.GO_FIELDS:
      check_go_int(go_name, getattr(self, name), go_type)
    self.attributes.check_types()

  def validate(self):
    """Go's `Validate()` for this type, preceded by the Go integer type checks."""
    self.check_types()
    self.attributes.validate()
    self.check()

  def check(self):
    """This type's own rules, in Go's order (attributes are already validated)."""
    raise NotImplementedError

  def body_elements(self) -> list[int]:
    """The hashed fields after `chain_id, tx_type, nonce, expired_at, account, api_key`."""
    raise NotImplementedError

  def body_json(self) -> dict[str, Any]:
    """This type's own JSON fields, between `ApiKeyIndex` and `ExpiredAt`."""
    raise NotImplementedError

  def hash(self, chain_id: int) -> bytes:
    """The 40-byte message hash Go's `Hash(lighterChainId)` returns (also the tx hash)."""
    elems = [
      chain_id,
      self.TX_TYPE,
      self.nonce,
      self.expired_at,
      self.account_index,
      self.api_key_index,
      *self.body_elements(),
    ]
    return self.attributes.aggregate(hash_to_fp5([from_go_int(x) for x in elems]))

  def l1_message(self, chain_id: int) -> str | None:
    """The EIP-191 message an L1 signature covers, for the types that can carry one."""
    return None

  def tx_info(self, sig: bytes, *, l1_sig: str = '') -> str:
    """`tx_info`, exactly as Go's `json.Marshal` of the signed struct."""
    return go_json(
      {
        self.ACCOUNT_KEY: self.account_index,
        'ApiKeyIndex': self.api_key_index,
        **self.body_json(),
        'ExpiredAt': self.expired_at,
        'Nonce': self.nonce,
        'Sig': b64(sig),
        'L2TxAttributes': self.attributes.to_json(),
      }
    )

  def sign(
    self,
    signer: MessageSigner,
    *,
    chain_id: int,
    l1_signature: str = '',
    verify_with: bytes | None = None,
  ) -> SignedTx:
    """Validate, hash, sign and encode (Go's `Construct*Tx` plus `GetTxInfo`).

    Args:
      signer: Signs the 40-byte hash with the API key of `api_key_index`.
      chain_id: Lighter chain id, mixed into the hash.
      l1_signature: `L1Sig`, for the types that carry one (`0x`-prefixed hex).
      verify_with: A public key to check the new signature against before returning, as
        Go's client does after signing a `ChangePubKey` or an `ApproveIntegrator`.

    Raises:
      BadRequest: The transaction breaks one of Go's validation rules (Go's message).
      LogicError: The signature does not verify under `verify_with`.
    """
    self.validate()
    msg_hash = self.hash(chain_id)
    sig = signer.sign(msg_hash)
    if verify_with is not None and not schnorr.verify(
      pk=verify_with, msg_hash=msg_hash, sig=sig
    ):
      raise LogicError('failed to validate signature')
    return SignedTx(
      tx_type=self.TX_TYPE,
      tx_info=self.tx_info(sig, l1_sig=l1_signature),
      tx_hash=msg_hash.hex(),
      message_to_sign=self.l1_message(chain_id),
    )


# ---------------------------------------------------------------- shared checks


def check_account(value: int, *, low: str, high: str, maximum: int = MAX_ACCOUNT_INDEX):
  """An account index in [-1, maximum]."""
  if value < MIN_ACCOUNT_INDEX:
    fail(low)
  if value > maximum:
    fail(high)


def check_api_key(value: int, *, allow_nil: bool = False):
  """An API key index <= 254 (or the nil key 255, where Go allows it)."""
  if value > MAX_API_KEY_INDEX and not (allow_nil and value == NIL_API_KEY_INDEX):
    fail(ERR_API_KEY_INDEX_TOO_HIGH)


def check_nonce_and_expiry(*, nonce: int, expired_at: int):
  """`AccountNonce >= 0`, and `ExpiredAt` within [0, 2^48 - 1]."""
  if nonce < 0:
    fail(ERR_NONCE_TOO_LOW)
  if expired_at < 0 or expired_at > MAX_TIMESTAMP:
    fail(ERR_EXPIRED_AT_INVALID)


def check_market(value: int):
  """A market index in [0, 32767], but not the nil market 255."""
  if value < 0 or value == NIL_MARKET_INDEX or value > MAX_MARKET_INDEX:
    fail(ERR_INVALID_MARKET_INDEX)


def check_asset(value: int):
  """An asset index in [1, 62]."""
  if value < MIN_ASSET_INDEX:
    fail(ERR_ASSET_INDEX_TOO_LOW)
  if value > MAX_ASSET_INDEX:
    fail(ERR_ASSET_INDEX_TOO_HIGH)


def check_route(value: int):
  """Route type 0 (perps) or 1 (spot)."""
  if value not in (0, 1):
    fail(ERR_ROUTE_TYPE_INVALID)
