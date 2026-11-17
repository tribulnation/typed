"""EIP-712 structs, action hashes and signature encodings: the pure half of RISEx signing.

Every signature shares one domain, `{name: "RISEx", version: "1", chainId,
verifyingContract}`, where `verifyingContract` is the Authorization contract
(`GET /v1/auth/eip712-domain`, `addresses.auth`). Struct type strings are hashed
literally, so the field lists below are copied verbatim from the contracts; their
typehashes are pinned by the unit tests against the values RISEx read off the mainnet
Authorization contract.

Trading actions are not structs of their own: each is reduced to an *action hash*
(`keccak256(abi.encode(keccak256("RISE_PERPS_<ACTION>_V1"), ...))`) that the signer key
signs inside one `VerifyWitness` permit.

References:
  - [Integration](https://developer.rise.trade/reference/integration)
"""

from typing_extensions import Any, Literal, TypedDict
import base64

from eth_abi.abi import encode
from eth_account.messages import encode_typed_data
from eth_account.signers.local import LocalAccount
from eth_utils.crypto import keccak

from .exc import BadRequest


class Field(TypedDict):
  """One member of an EIP-712 struct type."""

  name: str
  type: str


class Domain(TypedDict):
  """The EIP-712 domain every RISEx signature uses."""

  name: str
  version: str
  chainId: int
  verifyingContract: str


DOMAIN_TYPE: list[Field] = [
  {'name': 'name', 'type': 'string'},
  {'name': 'version', 'type': 'string'},
  {'name': 'chainId', 'type': 'uint256'},
  {'name': 'verifyingContract', 'type': 'address'},
]

StructName = Literal[
  'VerifyWitness',
  'RegisterSigner',
  'VerifySigner',
  'RevokeSigner',
  'PermitSingle',
  'Login',
  'RegisterV2',
]
"""Every struct the client signs."""

STRUCTS: dict[StructName, list[Field]] = {
  'VerifyWitness': [
    {'name': 'account', 'type': 'address'},
    {'name': 'target', 'type': 'address'},
    {'name': 'hash', 'type': 'bytes32'},
    {'name': 'nonceAnchor', 'type': 'uint48'},
    {'name': 'nonceBitmap', 'type': 'uint8'},
    {'name': 'deadline', 'type': 'uint32'},
  ],
  'RegisterSigner': [
    {'name': 'account', 'type': 'address'},
    {'name': 'signer', 'type': 'address'},
    {'name': 'message', 'type': 'string'},
    {'name': 'expiration', 'type': 'uint32'},
    {'name': 'nonceAnchor', 'type': 'uint48'},
    {'name': 'nonceBitmap', 'type': 'uint8'},
  ],
  'VerifySigner': [
    {'name': 'account', 'type': 'address'},
    {'name': 'nonceAnchor', 'type': 'uint48'},
    {'name': 'nonceBitmap', 'type': 'uint8'},
  ],
  'RevokeSigner': [
    {'name': 'account', 'type': 'address'},
    {'name': 'signer', 'type': 'address'},
    {'name': 'nonceAnchor', 'type': 'uint48'},
    {'name': 'nonceBitmap', 'type': 'uint8'},
  ],
  'PermitSingle': [
    {'name': 'account', 'type': 'address'},
    {'name': 'operator', 'type': 'address'},
    {'name': 'budget', 'type': 'uint96'},
    {'name': 'allowanceExpiry', 'type': 'uint32'},
    {'name': 'nonceAnchor', 'type': 'uint48'},
    {'name': 'nonceBitmap', 'type': 'uint8'},
  ],
  'Login': [
    {'name': 'account', 'type': 'address'},
    {'name': 'nonce', 'type': 'uint256'},
    {'name': 'deadline', 'type': 'uint32'},
  ],
  'RegisterV2': [
    {'name': 'signer', 'type': 'address'},
    {'name': 'message', 'type': 'string'},
    {'name': 'nonce', 'type': 'uint256'},
  ],
}
"""Struct definitions, in contract field order."""

MAX_NONCE_BIT = 207
"""Highest valid `nonceBitmap`: the field is a `uint8`, but 208 and above revert
`InvalidNonceIndex`."""


def type_string(name: StructName) -> str:
  """The canonical EIP-712 type string of a struct, e.g. `Login(address account,...)`."""
  fields = ','.join(f'{f["type"]} {f["name"]}' for f in STRUCTS[name])
  return f'{name}({fields})'


def sign_struct(
  key: LocalAccount, domain: Domain, name: StructName, message: dict[str, Any]
) -> tuple[bytes, int]:
  """Sign one struct, returning the 65-byte `r || s || v` signature and `v`.

  Args:
    key: The signing key (account or signer).
    domain: The RISEx EIP-712 domain.
    name: The struct's primary type.
    message: The struct's field values.
  """
  typed = {
    'types': {'EIP712Domain': DOMAIN_TYPE, name: STRUCTS[name]},
    'primaryType': name,
    'domain': domain,
    'message': message,
  }
  signed = key.sign_message(encode_typed_data(full_message=typed))
  return bytes(signed.signature), signed.v


def hex_signature(signature: bytes) -> str:
  """`0x`-hex encoding, used by setup and login signatures (`account_signature`, ...)."""
  return '0x' + signature.hex()


def compact_signature(signature: bytes, v: int) -> str:
  """Base64 of the 64-byte EIP-2098 compact form (`r || yParityAndS`), used by
  `permit.signature`, which the venue takes as base64-encoded bytes.
  """
  r, s = signature[:32], bytearray(signature[32:64])
  if v in (1, 28):
    s[0] |= 0x80
  return base64.b64encode(r + bytes(s)).decode()


def selector(action: str) -> bytes:
  """`keccak256` of an action's name, e.g. `RISE_PERPS_PLACE_ORDER_V1`."""
  return keccak(text=action)


def action_hash(action: str, types: list[str], values: list[Any]) -> bytes:
  """`keccak256(abi.encode(selector(action), *values))`, every operand a full word."""
  return keccak(encode(['bytes32', *types], [selector(action), *values]))


def pack_order(
  *,
  market_id: int,
  size_steps: int,
  price_ticks: int,
  side: int,
  post_only: bool,
  reduce_only: bool,
  stp_mode: int,
  order_type: int,
  time_in_force: int,
) -> int:
  """Pack an order into the router's `uint88`, MSB to LSB: market id (16 bits), size
  steps (32), price ticks (24), order flags (8), version 1 (5), reserved (1).

  Raises:
    BadRequest: A field exceeds its bit width.
  """
  limits = {
    'market_id': (market_id, 16),
    'size_steps': (size_steps, 32),
    'price_ticks': (price_ticks, 24),
    'side': (side, 1),
    'stp_mode': (stp_mode, 2),
    'order_type': (order_type, 1),
    'time_in_force': (time_in_force, 2),
  }
  for name, (value, bits) in limits.items():
    if not 0 <= value < 1 << bits:
      raise BadRequest(f'`{name}` must fit in {bits} unsigned bits, got {value}')
  flags = (
    side
    | int(post_only) << 1
    | int(reduce_only) << 2
    | stp_mode << 3
    | order_type << 5
    | time_in_force << 6
  )
  return market_id << 70 | size_steps << 38 | price_ticks << 14 | flags << 6 | 1 << 1


def place_order_hash(
  order_data: int,
  *,
  builder_id: int = 0,
  builder_fee_bps: int = 0,
  client_order_id: int = 0,
  ttl_units: int = 0,
) -> bytes:
  """Action hash of `POST /v1/orders/place`.

  The header-flags byte says which optional fields are present (`0x01` permit, always;
  `0x02` builder; `0x04` client order id; `0x10` TTL), and the `builderFeeBps` word is
  only encoded when non-zero.
  """
  flags = (
    0x01
    | (0x02 if builder_id else 0)
    | (0x04 if client_order_id else 0)
    | (0x10 if ttl_units else 0)
  )
  types = ['uint8', 'uint88', 'uint16']
  values: list[Any] = [flags, order_data, builder_id]
  if builder_fee_bps:
    types.append('uint16')
    values.append(builder_fee_bps)
  types += ['uint64', 'uint16']
  values += [client_order_id, ttl_units]
  return action_hash('RISE_PERPS_PLACE_ORDER_V1', types, values)


def resting_order_id(order_id: str) -> int:
  """The on-chain resting order id a cancel commits to, from the composite `order_id`.

  `order_id` is 24 bytes of hex: wide order id, block number, log index (8 bytes each);
  the resting order id is `wide_order_id >> 1`.

  Raises:
    BadRequest: `order_id` is not a 24-byte hex string.
  """
  raw = order_id.removeprefix('0x')
  if len(raw) != 48:
    raise BadRequest(f'`order_id` must be 24 bytes of hex, got {order_id!r}')
  try:
    wide = int(raw[:16], 16)
  except ValueError as e:
    raise BadRequest(f'`order_id` must be hex, got {order_id!r}') from e
  return wide >> 1
