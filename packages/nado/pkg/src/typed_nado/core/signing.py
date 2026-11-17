"""EIP-712 signing of Nado payloads.

Every signed payload is one struct in the `{name: "Nado", version: "0.0.1", chainId,
verifyingContract}` domain. `verifyingContract` is the Endpoint contract for everything
except orders, which verify against `address(product_id)` (product 18 gives
`0x0000000000000000000000000000000000000012`).

Signing works on wire-format dicts: what is signed is exactly what is sent. Wire values are
strings for every integer wider than 32 bits (x18 prices and amounts, nonces, expirations),
plain numbers for `uint32` fields (`productId`, `productIds`) and hex strings for `bytes32`
and `address` fields; the signature uses the Solidity type of each field instead.
"""

from typing_extensions import Any, Awaitable, Callable, Literal, Mapping, TypedDict
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
import secrets

from eth_account.messages import SignableMessage, encode_typed_data
from eth_utils.address import is_address, to_checksum_address
from eth_utils.crypto import keccak

from .auth import Credentials
from .exc import AuthError, BadRequest, LogicError
from .types import timestamp_millis


class Field(TypedDict):
  """One member of an EIP-712 struct type."""

  name: str
  type: str


DOMAIN_FIELDS: list[Field] = [
  {'name': 'name', 'type': 'string'},
  {'name': 'version', 'type': 'string'},
  {'name': 'chainId', 'type': 'uint256'},
  {'name': 'verifyingContract', 'type': 'address'},
]

DOMAIN_NAME = 'Nado'
DOMAIN_VERSION = '0.0.1'

STRUCTS: dict[str, list[Field]] = {
  'Order': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'priceX18', 'type': 'int128'},
    {'name': 'amount', 'type': 'int128'},
    {'name': 'expiration', 'type': 'uint64'},
    {'name': 'nonce', 'type': 'uint64'},
    {'name': 'appendix', 'type': 'uint128'},
  ],
  'Cancellation': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'productIds', 'type': 'uint32[]'},
    {'name': 'digests', 'type': 'bytes32[]'},
    {'name': 'nonce', 'type': 'uint64'},
  ],
  'CancellationProducts': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'productIds', 'type': 'uint32[]'},
    {'name': 'nonce', 'type': 'uint64'},
  ],
  'WithdrawCollateral': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'productId', 'type': 'uint32'},
    {'name': 'amount', 'type': 'uint128'},
    {'name': 'nonce', 'type': 'uint64'},
  ],
  'WithdrawCollateralV2': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'productId', 'type': 'uint32'},
    {'name': 'amount', 'type': 'uint128'},
    {'name': 'nonce', 'type': 'uint64'},
    {'name': 'sendTo', 'type': 'address'},
    {'name': 'appendix', 'type': 'uint128'},
  ],
  'TransferQuote': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'recipient', 'type': 'bytes32'},
    {'name': 'amount', 'type': 'uint128'},
    {'name': 'nonce', 'type': 'uint64'},
  ],
  'LiquidateSubaccount': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'liquidatee', 'type': 'bytes32'},
    {'name': 'productId', 'type': 'uint32'},
    {'name': 'isEncodedSpread', 'type': 'bool'},
    {'name': 'amount', 'type': 'int128'},
    {'name': 'nonce', 'type': 'uint64'},
  ],
  'MintNlp': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'quoteAmount', 'type': 'uint128'},
    {'name': 'nonce', 'type': 'uint64'},
  ],
  'BurnNlp': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'nlpAmount', 'type': 'uint128'},
    {'name': 'nonce', 'type': 'uint64'},
  ],
  'LinkSigner': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'signer', 'type': 'bytes32'},
    {'name': 'nonce', 'type': 'uint64'},
  ],
  'DependencyUpdate': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'oldDigest', 'type': 'bytes32'},
    {'name': 'newDigest', 'type': 'bytes32'},
    {'name': 'nonce', 'type': 'uint64'},
  ],
  'ListTriggerOrders': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'recvTime', 'type': 'uint64'},
  ],
  'StreamAuthentication': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'expiration', 'type': 'uint64'},
  ],
  'LeaderboardAuthentication': [
    {'name': 'sender', 'type': 'bytes32'},
    {'name': 'expiration', 'type': 'uint64'},
    {'name': 'contestIds', 'type': 'uint32[]'},
  ],
}
"""Every signed struct, field order and Solidity types exactly as the docs' signing page and
the official SDKs declare them. `MintNlp` carries no `productId`: the docs' Solidity listing
shows one, but their own JSON type, both SDKs and the docs' example omit it."""

SignKind = Literal[
  'place_order',
  'place_orders',
  'cancel_orders',
  'cancel_product_orders',
  'cancel_and_place',
  'withdraw_collateral',
  'withdraw_collateral_v2',
  'transfer_quote',
  'liquidate_subaccount',
  'mint_nlp',
  'burn_nlp',
  'link_signer',
  'update_dependency',
  'list_trigger_orders',
  'leaderboard',
]
"""How the core signs a call's body (`meta.sign`):

- `place_order`: `order` signed as `Order`, against `address(product_id)`, into `signature`.
- `place_orders`: each element of `orders`, as `place_order`.
- `cancel_orders`, `cancel_product_orders`: `tx` as `Cancellation`/`CancellationProducts`.
- `cancel_and_place`: `cancel_tx` as `Cancellation` into `cancel_signature`, and
  `place_order` as `place_order`.
- `withdraw_collateral`, `withdraw_collateral_v2`, `transfer_quote` (also its v2 execute),
  `liquidate_subaccount`, `mint_nlp`, `burn_nlp`, `link_signer`: `tx` as the matching struct.
- `update_dependency`: `tx` as `DependencyUpdate` (trigger service).
- `list_trigger_orders`: `tx` as `ListTriggerOrders` (trigger service, a signed read); `tx`
  itself defaults to `{}`, since the core fills both of its fields.
- `leaderboard`: `update_registration.tx` as `LeaderboardAuthentication` (rewards).
"""

TX_STRUCTS: dict[str, str] = {
  'cancel_orders': 'Cancellation',
  'cancel_product_orders': 'CancellationProducts',
  'withdraw_collateral': 'WithdrawCollateral',
  'withdraw_collateral_v2': 'WithdrawCollateralV2',
  'transfer_quote': 'TransferQuote',
  'liquidate_subaccount': 'LiquidateSubaccount',
  'mint_nlp': 'MintNlp',
  'burn_nlp': 'BurnNlp',
  'link_signer': 'LinkSigner',
  'update_dependency': 'DependencyUpdate',
  'list_trigger_orders': 'ListTriggerOrders',
}
"""Kinds whose whole payload is one `{tx, signature}` pair at the top of the body."""

TX_NONCE_KINDS: frozenset[str] = frozenset(
  {
    'withdraw_collateral',
    'withdraw_collateral_v2',
    'transfer_quote',
    'liquidate_subaccount',
    'mint_nlp',
    'burn_nlp',
    'link_signer',
  }
)
"""Kinds whose `nonce` is the wallet's sequential `tx_nonce` (the `nonces` query), as the
official SDKs do. Orders, cancellations and trigger executes take a time-based order nonce
instead (`Signer.order_nonce`)."""

ORDER_NONCE_STRUCTS: frozenset[str] = frozenset(
  {
    'Order',
    'Cancellation',
    'CancellationProducts',
    'DependencyUpdate',
  }
)
"""Structs whose missing `nonce` is filled with a fresh order nonce."""

DEFAULT_RECV_WINDOW = timedelta(seconds=90)
"""How far ahead of now generated deadlines sit: the time part of order nonces (after which
the engine discards the order), `recvTime` and authentication `expiration`s. The official
SDKs use 90 s; the venue rejects anything more than 100 s ahead."""


def order_verifying_contract(product_id: int) -> str:
  """The EIP-712 `verifyingContract` of an order: `address(product_id)`, the product id as a
  20-byte big-endian address.

  Args:
    product_id: The order's product.
  """
  return to_checksum_address('0x' + product_id.to_bytes(20, 'big').hex())


def integer(value: Any, field: str) -> int:
  """An integer field's value, from an `int`, an integral `Decimal` or a numeral string.

  Raises:
    BadRequest: The value is not an integer (floats are refused: they lose precision; a
      `NaN` or infinite `Decimal` is refused before conversion).
  """
  if isinstance(value, bool) or isinstance(value, float):
    raise BadRequest(f'{field} must be an integer, got {value!r}')
  if isinstance(value, int):
    return value
  if isinstance(value, Decimal) and not value.is_finite():
    raise BadRequest(f'{field} must be a finite integer, got {value!r}')
  if isinstance(value, Decimal) and value == value.to_integral_value():
    return int(value)
  if isinstance(value, str):
    try:
      return int(value, 0) if value.startswith(('0x', '0X')) else int(value)
    except ValueError:
      pass
  raise BadRequest(f'{field} must be an integer, got {value!r}')


DIGEST_FIELDS = frozenset({'digests', 'oldDigest', 'newDigest'})
"""`bytes32` fields holding an order digest: a hash, so exactly 32 bytes, never padded."""


def bytes32(value: Any, field: str, *, exact: bool = False) -> bytes:
  """A `bytes32` field's value, from hex or bytes, right-padded with zeros like the docs'
  own `hex_to_bytes32` (a subaccount, say: an address plus a short name).

  Args:
    value: Hex (with or without `0x`) or raw bytes.
    field: Field path, for error messages.
    exact: Require exactly 32 bytes instead of padding (an order digest).

  Raises:
    BadRequest: The value is not hex of at most 32 bytes (exactly 32 when `exact`).
  """
  if isinstance(value, str):
    try:
      raw = bytes.fromhex(value[2:] if value.startswith(('0x', '0X')) else value)
    except ValueError:
      raise BadRequest(f'{field} must be hex, got {value!r}') from None
  elif isinstance(value, bytes):
    raw = value
  else:
    raise BadRequest(f'{field} must be hex, got {value!r}')
  if len(raw) > 32:
    raise BadRequest(f'{field} is longer than 32 bytes')
  if exact and len(raw) != 32:
    raise BadRequest(f'{field} must be exactly 32 bytes, got {len(raw)}')
  return raw.ljust(32, b'\0')


def scalar(type: str, value: Any, field: str) -> tuple[Any, Any]:
  """One field's `(wire, signable)` values, for its Solidity `type`.

  Raises:
    BadRequest: The value does not fit the type.
  """
  if type == 'bytes32':
    raw = bytes32(value, field, exact=field.rsplit('.', 1)[-1] in DIGEST_FIELDS)
    return '0x' + raw.hex(), raw
  if type == 'address':
    if not isinstance(value, str) or not is_address(value):
      raise BadRequest(f'{field} must be an address, got {value!r}')
    return value, to_checksum_address(value)
  if type == 'bool':
    if not isinstance(value, bool):
      raise BadRequest(f'{field} must be a boolean, got {value!r}')
    return value, value
  if type == 'string':
    return str(value), str(value)
  if type.startswith(('uint', 'int')):
    number = integer(value, field)
    bits = int(type.removeprefix('u').removeprefix('int'))
    low, high = (
      (0, 2**bits) if type.startswith('u') else (-(2 ** (bits - 1)), 2 ** (bits - 1))
    )
    if not low <= number < high:
      raise BadRequest(f'{field} is out of range for {type}: {number}')
    # Numbers up to 32 bits travel as JSON numbers; wider ones as strings, as the docs show.
    return (number if bits <= 32 else str(number)), number
  raise LogicError(f'Unsupported EIP-712 type {type!r} on {field}')


def encode(
  primary: str, tx: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
  """A struct's `(wire, signable)` dicts: every declared field, in canonical wire form and as
  the signature encodes it. Undeclared keys are kept on the wire, unsigned.

  Raises:
    BadRequest: A declared field is missing or does not fit its type.
  """
  wire: dict[str, Any] = dict(tx)
  signable: dict[str, Any] = {}
  for f in STRUCTS[primary]:
    name, type = f['name'], f['type']
    if tx.get(name) is None:
      raise BadRequest(f'{primary}.{name} is required')
    value = tx[name]
    if type.endswith('[]'):
      if not isinstance(value, list | tuple):
        raise BadRequest(f'{primary}.{name} must be a list, got {value!r}')
      pairs = [scalar(type[:-2], item, f'{primary}.{name}') for item in value]
      wire[name] = [w for w, _ in pairs]
      signable[name] = [s for _, s in pairs]
    else:
      wire[name], signable[name] = scalar(type, value, f'{primary}.{name}')
  return wire, signable


def message_hash(signable: SignableMessage) -> str:
  """The 32-byte EIP-712 hash an EIP-191 version-1 message signs: for an `Order`, its
  digest (the id the engine reports and cancels by)."""
  return (
    '0x' + keccak(b'\x19' + signable.version + signable.header + signable.body).hex()
  )


@dataclass(frozen=True, kw_only=True)
class Signer:
  """Signs payloads for one client: its key, the deployment's domain, and its default
  sender."""

  credentials: Credentials
  """The signing key and the default subaccount."""
  chain_id: int
  """The deployment's EIP-712 `chainId`."""
  endpoint_address: str
  """The Endpoint contract, `verifyingContract` of everything but orders."""
  recv_window: timedelta = DEFAULT_RECV_WINDOW
  """How far ahead of now generated deadlines sit."""

  def typed_data(
    self, primary: str, signable: Mapping[str, Any], *, verifying_contract: str
  ) -> dict[str, Any]:
    """The full EIP-712 typed-data document of one struct.

    Args:
      primary: The struct's type name.
      signable: Its values, as `encode` returns them for signing.
      verifying_contract: The domain's `verifyingContract`.
    """
    return {
      'types': {'EIP712Domain': DOMAIN_FIELDS, primary: STRUCTS[primary]},
      'primaryType': primary,
      'domain': {
        'name': DOMAIN_NAME,
        'version': DOMAIN_VERSION,
        'chainId': self.chain_id,
        'verifyingContract': verifying_contract,
      },
      'message': dict(signable),
    }

  def sign(
    self, primary: str, tx: Mapping[str, Any], *, verifying_contract: str | None = None
  ) -> tuple[dict[str, Any], str, str]:
    """Sign one struct.

    Args:
      primary: The struct's type name.
      tx: Its values, in wire or Python form.
      verifying_contract: The domain's `verifyingContract`; the Endpoint contract when
        omitted.

    Returns:
      The struct in canonical wire form, the `0x`-prefixed 65-byte signature and the
      struct's EIP-712 hash (an order's digest).

    Raises:
      BadRequest: A field is missing or does not fit its type.
    """
    wire, signable = encode(primary, tx)
    contract = verifying_contract or self.endpoint_address
    message = encode_typed_data(
      full_message=self.typed_data(primary, signable, verifying_contract=contract)
    )
    signed = self.credentials.account.sign_message(message)
    return wire, '0x' + bytes(signed.signature).hex(), message_hash(message)

  def deadline(self) -> int:
    """Epoch milliseconds `recv_window` from now."""
    return timestamp_millis.now() + int(self.recv_window.total_seconds() * 1000)

  def order_nonce(self) -> str:
    """A fresh order nonce: the discard deadline (epoch ms) in the top 44 bits, 20 random
    bits below it to keep otherwise identical orders apart."""
    return str((self.deadline() << 20) | secrets.randbelow(1 << 20))

  def with_defaults(self, primary: str, tx: Mapping[str, Any]) -> dict[str, Any]:
    """`tx` with whatever the core fills when absent: `sender` (the client's subaccount), an
    order nonce, a `recvTime` or an `expiration` deadline."""
    filled = dict(tx)
    if filled.get('sender') is None:
      filled['sender'] = self.credentials.sender
    if primary in ORDER_NONCE_STRUCTS and filled.get('nonce') is None:
      filled['nonce'] = self.order_nonce()
    if primary == 'ListTriggerOrders' and filled.get('recvTime') is None:
      filled['recvTime'] = str(self.deadline())
    if (
      primary in ('StreamAuthentication', 'LeaderboardAuthentication')
      and filled.get('expiration') is None
    ):
      filled['expiration'] = str(self.deadline())
    return filled

  def sign_order(self, params: Mapping[str, Any]) -> dict[str, Any]:
    """Sign one `place_order` body (`{product_id, order, ...}`) into its `signature`."""
    if not isinstance(params.get('order'), Mapping):
      raise BadRequest('place_order.order is required')
    product_id = integer(params.get('product_id'), 'place_order.product_id')
    order, signature, _ = self.sign(
      'Order',
      self.with_defaults('Order', params['order']),
      verifying_contract=order_verifying_contract(product_id),
    )
    return {**params, 'order': order, 'signature': signature}

  def sign_tx(
    self,
    primary: str,
    container: Mapping[str, Any],
    *,
    tx_key: str = 'tx',
    signature_key: str = 'signature',
  ) -> dict[str, Any]:
    """Sign the struct under `container[tx_key]` into `container[signature_key]`."""
    if not isinstance(container.get(tx_key), Mapping):
      raise BadRequest(f'{tx_key} is required')
    tx, signature, _ = self.sign(
      primary, self.with_defaults(primary, container[tx_key])
    )
    return {**container, tx_key: tx, signature_key: signature}


def needs_tx_nonce(kind: SignKind, body: Mapping[str, Any]) -> bool:
  """Whether signing `body` needs the wallet's next `tx_nonce`, fetched first."""
  if kind not in TX_NONCE_KINDS:
    return False
  tx = body.get('tx')
  return not isinstance(tx, Mapping) or tx.get('nonce') is None


async def prepare(
  kind: SignKind,
  body: Mapping[str, Any],
  signer: Signer,
  tx_nonce: Callable[[], Awaitable[str]],
) -> dict[str, Any]:
  """Fill and sign one call's body.

  Args:
    kind: How to sign it (`SignKind`).
    body: The call's wire values.
    signer: The client's signer.
    tx_nonce: Fetches the wallet's next `tx_nonce`; only awaited when a sequential-nonce
      payload carries none.

  Raises:
    BadRequest: A signed field is missing or does not fit its type.
  """
  if kind == 'place_order':
    return signer.sign_order(body)
  if kind == 'place_orders':
    orders = body.get('orders')
    if not isinstance(orders, list | tuple):
      raise BadRequest('place_orders.orders is required')
    return {**body, 'orders': [signer.sign_order(order) for order in orders]}
  if kind == 'cancel_and_place':
    if not isinstance(body.get('place_order'), Mapping):
      raise BadRequest('cancel_and_place.place_order is required')
    signed = signer.sign_tx(
      'Cancellation', body, tx_key='cancel_tx', signature_key='cancel_signature'
    )
    return {**signed, 'place_order': signer.sign_order(body['place_order'])}
  if kind == 'leaderboard':
    container = body.get('update_registration')
    if not isinstance(container, Mapping):
      raise BadRequest('update_registration is required')
    return {
      **body,
      'update_registration': signer.sign_tx('LeaderboardAuthentication', container),
    }
  primary = TX_STRUCTS[kind]
  if kind == 'list_trigger_orders' and body.get('tx') is None:
    # Every `ListTriggerOrders` field is filled by the core, so the struct is optional.
    body = {**body, 'tx': {}}
  if needs_tx_nonce(kind, body):
    tx = body.get('tx')
    if not isinstance(tx, Mapping):
      raise BadRequest(f'{kind}.tx is required')
    body = {**body, 'tx': {**tx, 'nonce': await tx_nonce()}}
  return signer.sign_tx(primary, body)


def with_default_subaccount(
  name: str, values: Mapping[str, Any], field: str | None, signer: Signer | None
) -> dict[str, Any]:
  """`values` with `field` (`subaccount` or `sender`) set to the client's own subaccount
  when the caller left it out; `values` unchanged when `field` is `None`.

  Args:
    name: The call or stream, for the error message.
    values: The call's wire values.
    field: The request field naming the subaccount (`meta.default_subaccount`).
    signer: The client's signer, `None` for a public client.

  Raises:
    AuthError: The field is absent and the client has no subaccount (`public=True`).
  """
  if field is None or values.get(field) is not None:
    return dict(values)
  if signer is None:
    raise AuthError(
      f'{name}: pass `{field}`; this client was built with `public=True` and has no'
      ' default subaccount.'
    )
  return {**values, field: signer.credentials.sender}
