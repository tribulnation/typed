"""EIP-712 action signatures.

Every order create/replace/close, TP/SL create, withdraw and API-key creation carries a
`signature` over one struct in the `{name: "EVEDEX", version: "2", chainId, salt}` domain
(no `verifyingContract`). Before signing, every decimal is rounded to 8 places and sent in
that form, and the signed struct carries it scaled to an integer (`x * 1e8`). Order
creates and closes also carry the domain's `chainId` in the struct and, as a string, in the
body.

Mirrors `@evedex/exchange-crypto` 1.1.5 (`utils/crypto.js`, `orders.js`); the test vectors
in `test/test_signing.py` were produced by that package.
"""

from typing_extensions import Any, Literal, Mapping, TypedDict
from datetime import datetime, timezone
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal, InvalidOperation
import secrets

from eth_account.messages import encode_typed_data
from eth_account.signers.local import LocalAccount

from .exc import LogicError

Action = Literal[
  'new_limit_order',
  'new_market_order',
  'new_stop_limit_order',
  'position_close_order',
  'new_take_profit_stop_loss',
  'replace_limit_order',
  'replace_stop_limit_order',
  'withdraw',
  'oauth_consent',
  'create_new_api_key',
]
"""The EIP-712 primary type of a signed request."""


class Field(TypedDict):
  """One member of an EIP-712 struct type."""

  name: str
  type: str


DOMAIN_NAME = 'EVEDEX'
DOMAIN_VERSION = '2'
DOMAIN_SALT = '0x5792f7333c35db190e30acc144f049fd15b24f552c0010b8b3e06f9105c37c5a'

DOMAIN_FIELDS: list[Field] = [
  {'name': 'name', 'type': 'string'},
  {'name': 'version', 'type': 'string'},
  {'name': 'chainId', 'type': 'uint256'},
  {'name': 'salt', 'type': 'bytes32'},
]

STRUCTS: dict[Action, list[Field]] = {
  'new_limit_order': [
    {'name': 'id', 'type': 'string'},
    {'name': 'instrument', 'type': 'string'},
    {'name': 'side', 'type': 'string'},
    {'name': 'leverage', 'type': 'uint8'},
    {'name': 'quantity', 'type': 'uint96'},
    {'name': 'limitPrice', 'type': 'uint80'},
    {'name': 'chainId', 'type': 'uint256'},
  ],
  'new_market_order': [
    {'name': 'id', 'type': 'string'},
    {'name': 'instrument', 'type': 'string'},
    {'name': 'side', 'type': 'string'},
    {'name': 'timeInForce', 'type': 'string'},
    {'name': 'leverage', 'type': 'uint8'},
    {'name': 'cashQuantity', 'type': 'uint96'},
    {'name': 'chainId', 'type': 'uint256'},
  ],
  'new_stop_limit_order': [
    {'name': 'id', 'type': 'string'},
    {'name': 'instrument', 'type': 'string'},
    {'name': 'side', 'type': 'string'},
    {'name': 'leverage', 'type': 'uint8'},
    {'name': 'quantity', 'type': 'uint96'},
    {'name': 'limitPrice', 'type': 'uint80'},
    {'name': 'stopPrice', 'type': 'uint80'},
    {'name': 'chainId', 'type': 'uint256'},
  ],
  'position_close_order': [
    {'name': 'id', 'type': 'string'},
    {'name': 'instrument', 'type': 'string'},
    {'name': 'leverage', 'type': 'uint8'},
    {'name': 'quantity', 'type': 'uint96'},
    {'name': 'chainId', 'type': 'uint256'},
  ],
  'new_take_profit_stop_loss': [
    {'name': 'instrument', 'type': 'string'},
    {'name': 'type', 'type': 'string'},
    {'name': 'side', 'type': 'string'},
    {'name': 'quantity', 'type': 'uint96'},
    {'name': 'price', 'type': 'uint80'},
  ],
  'replace_limit_order': [
    {'name': 'orderId', 'type': 'string'},
    {'name': 'quantity', 'type': 'uint96'},
    {'name': 'limitPrice', 'type': 'uint80'},
  ],
  'replace_stop_limit_order': [
    {'name': 'orderId', 'type': 'string'},
    {'name': 'quantity', 'type': 'uint96'},
    {'name': 'limitPrice', 'type': 'uint80'},
    {'name': 'stopPrice', 'type': 'uint80'},
  ],
  'withdraw': [
    {'name': 'recipient', 'type': 'address'},
    {'name': 'amount', 'type': 'uint256'},
  ],
  'oauth_consent': [
    {'name': 'oauthRequestId', 'type': 'string'},
  ],
  'create_new_api_key': [
    {'name': 'expireAt', 'type': 'uint64'},
    {'name': 'scopes', 'type': 'string'},
  ],
}

DECIMAL_FIELDS = frozenset(
  {'quantity', 'limitPrice', 'stopPrice', 'cashQuantity', 'price', 'amount'}
)
"""Struct members that are decimals on the wire and scaled integers in the signature."""

PRECISION = 8
"""Decimal places of the matching engine (`MATCHER_PRECISION`)."""

QUANTUM = Decimal(1).scaleb(-PRECISION)
SCALE = 10**PRECISION

ORDER_ID_EPOCH = datetime(2025, 7, 24, tzinfo=timezone.utc)
"""Day zero of the `DDDDD:` prefix of a v2 order id."""

ID_ACTIONS = frozenset(
  {
    'new_limit_order',
    'new_market_order',
    'new_stop_limit_order',
    'position_close_order',
  }
)
"""Actions whose body carries a client-generated order `id`."""


def expire_at(value: datetime | str | int) -> tuple[str, int]:
  """An API key's expiry as the wire wants it (RFC 3339) and as it is signed (epoch seconds).

  *Verified* on demo (2026-11-19): `expireAt: "2027-01-15T08:00:00.000Z"` signed as
  `1800000000` is accepted; a number on the wire is refused (`Expected string`), and a
  different signed value is refused `invalid_signature_error`.

  Raises:
    LogicError: `value` is not a datetime, an RFC 3339 string or epoch seconds.
  """
  if isinstance(value, int):
    moment = datetime.fromtimestamp(value, timezone.utc)
  elif isinstance(value, str):
    try:
      moment = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
      raise LogicError(f'Invalid expireAt: {value!r}') from None
  else:
    moment = value
  if moment.tzinfo is None:
    moment = moment.replace(tzinfo=timezone.utc)
  moment = moment.astimezone(timezone.utc)
  wire = moment.strftime('%Y-%m-%dT%H:%M:%S.') + f'{moment.microsecond // 1000:03d}Z'
  return wire, int(moment.timestamp())


def round_decimal(
  value: Decimal | int | str, *, rounding: str = ROUND_HALF_UP
) -> Decimal:
  """Round a decimal to the engine's 8 places, half-up (or down, for withdrawals).

  Raises:
    LogicError: `value` is not a finite non-negative number.
  """
  try:
    d = Decimal(value) if isinstance(value, (str, int)) else value
    rounded = d.quantize(QUANTUM, rounding=rounding)
  except (InvalidOperation, TypeError):
    raise LogicError(f'Invalid decimal: {value!r}') from None
  if not rounded.is_finite() or rounded < 0:
    raise LogicError(f'Invalid decimal: {value!r}')
  return rounded


def wire_decimal(value: Decimal) -> str:
  """A rounded decimal as its plain wire string, trailing zeros dropped (`0.001`)."""
  text = format(value, 'f')
  if '.' in text:
    text = text.rstrip('0').rstrip('.')
  return text or '0'


def order_id(now: datetime | None = None) -> str:
  """A fresh v2 order id, `DDDDD:<26 hex>`: days since 2025-07-24, then random hex.

  The venue rejects a prefix older than yesterday (`Invalid order ID date`), so an id is
  generated right before it is sent.
  """
  now = now or datetime.now(timezone.utc)
  days = (now - ORDER_ID_EPOCH).days
  return f'{days:05d}:{secrets.token_hex(13)}'


def typed_data(action: Action, message: Mapping[str, Any], *, chain_id: int) -> dict:
  """The full EIP-712 document for one struct, as `encode_typed_data` takes it."""
  return {
    'types': {'EIP712Domain': DOMAIN_FIELDS, action: STRUCTS[action]},
    'primaryType': action,
    'domain': {
      'name': DOMAIN_NAME,
      'version': DOMAIN_VERSION,
      'chainId': chain_id,
      'salt': DOMAIN_SALT,
    },
    'message': dict(message),
  }


def sign_typed(
  account: LocalAccount, action: Action, message: Mapping[str, Any], *, chain_id: int
) -> str:
  """Sign one struct and return the `0x`-prefixed 65-byte signature (`v` is 27 or 28)."""
  signable = encode_typed_data(
    full_message=typed_data(action, message, chain_id=chain_id)
  )
  return '0x' + account.sign_message(signable).signature.hex().removeprefix('0x')


def sign_action(
  account: LocalAccount, action: Action, body: Mapping[str, Any], *, chain_id: int
) -> dict[str, Any]:
  """Normalize a request body, sign it, and return the body to send.

  - every decimal struct member is rounded to 8 places (withdraw amounts down, the rest
    half-up) and sent as a plain string; the signature covers it scaled by `1e8`
  - an order create or close without an `id` gets a fresh one (`order_id`)
  - a struct with `chainId` gets the domain's chain id, sent as a string
  - `create_new_api_key`'s `scopes` list is signed comma-joined, and its `expireAt` is sent
    RFC 3339 and signed as epoch seconds (`expire_at`); `None` (never) is sent `null` and
    signed `0` (unverified)
  - every other body field (`postOnly`, `timeInForce` on a limit order, `tpsl`, ...) is
    sent unchanged and not signed

  Args:
    account: The wallet signing for the account.
    action: The struct to sign.
    body: The request body, without `signature`.
    chain_id: The environment's chain id.

  Raises:
    LogicError: A struct member is missing, or a decimal is invalid.
  """
  wire = dict(body)
  if action in ID_ACTIONS and not wire.get('id'):
    wire['id'] = order_id()
  message: dict[str, Any] = {}
  for field in STRUCTS[action]:
    name = field['name']
    if name == 'chainId':
      wire['chainId'] = str(chain_id)
      message[name] = chain_id
      continue
    if name == 'expireAt' and action == 'create_new_api_key' and wire.get(name) is None:
      wire[name] = None
      message[name] = 0
      continue
    if name not in wire or wire[name] is None:
      raise LogicError(f'Missing field {name!r} for a signed {action!r}')
    value = wire[name]
    if name in DECIMAL_FIELDS:
      rounding = ROUND_DOWN if action == 'withdraw' else ROUND_HALF_UP
      rounded = round_decimal(value, rounding=rounding)
      wire[name] = wire_decimal(rounded)
      message[name] = int(rounded * SCALE)
    elif (
      action == 'create_new_api_key' and name == 'scopes' and not isinstance(value, str)
    ):
      message[name] = ','.join(value)
    elif action == 'create_new_api_key' and name == 'expireAt':
      wire[name], message[name] = expire_at(value)
    else:
      message[name] = value
  wire['signature'] = sign_typed(account, action, message, chain_id=chain_id)
  return wire
