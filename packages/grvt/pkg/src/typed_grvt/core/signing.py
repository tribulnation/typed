"""EIP-712 signing of GRVT payloads: orders, transfers, withdrawals, derisk ratio, position
margin config and isolated margin, wallet login.

Every signed payload carries a `Signature{signer, r, s, v, expiration, nonce, chain_id}`
over a typed struct in the `{name: "GRVT Exchange", version: "0", chainId}` domain (no
`verifyingContract`). Signing works on wire-format dicts (strings for 64-bit integers and
decimals, exactly as sent), so what is signed is what goes on the wire.
"""

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal, InvalidOperation
import re
import secrets
import time

from eth_account import Account
from eth_account.messages import encode_typed_data
from eth_account.signers.local import LocalAccount
from typing_extensions import Any, Mapping, TypedDict

from typed_core.decimals import plain
from typed_core.exceptions import AuthError, BadRequest


class Field(TypedDict):
  """One member of an EIP-712 struct type."""

  name: str
  type: str


ORDER_LEG: list[Field] = [
  {'name': 'assetID', 'type': 'uint256'},
  {'name': 'contractSize', 'type': 'uint64'},
  {'name': 'limitPrice', 'type': 'uint64'},
  {'name': 'isBuyingContract', 'type': 'bool'},
]
ORDER_TYPES: dict[str, list[Field]] = {
  'Order': [
    {'name': 'subAccountID', 'type': 'uint64'},
    {'name': 'isMarket', 'type': 'bool'},
    {'name': 'timeInForce', 'type': 'uint8'},
    {'name': 'postOnly', 'type': 'bool'},
    {'name': 'reduceOnly', 'type': 'bool'},
    {'name': 'legs', 'type': 'OrderLeg[]'},
    {'name': 'nonce', 'type': 'uint32'},
    {'name': 'expiration', 'type': 'int64'},
  ],
  'OrderLeg': ORDER_LEG,
}
ORDER_WITH_BUILDER_FEE_TYPES: dict[str, list[Field]] = {
  'OrderWithBuilderFee': [
    *ORDER_TYPES['Order'][:6],
    {'name': 'builder', 'type': 'address'},
    {'name': 'builderFee', 'type': 'uint32'},
    *ORDER_TYPES['Order'][6:],
  ],
  'OrderLeg': ORDER_LEG,
}
TRANSFER_TYPES: dict[str, list[Field]] = {
  'Transfer': [
    {'name': 'fromAccount', 'type': 'address'},
    {'name': 'fromSubAccount', 'type': 'uint64'},
    {'name': 'toAccount', 'type': 'address'},
    {'name': 'toSubAccount', 'type': 'uint64'},
    {'name': 'tokenCurrency', 'type': 'uint8'},
    {'name': 'numTokens', 'type': 'uint64'},
    {'name': 'nonce', 'type': 'uint32'},
    {'name': 'expiration', 'type': 'int64'},
  ]
}
WITHDRAWAL_TYPES: dict[str, list[Field]] = {
  'Withdrawal': [
    {'name': 'fromAccount', 'type': 'address'},
    {'name': 'toEthAddress', 'type': 'address'},
    {'name': 'tokenCurrency', 'type': 'uint8'},
    {'name': 'numTokens', 'type': 'uint64'},
    {'name': 'nonce', 'type': 'uint32'},
    {'name': 'expiration', 'type': 'int64'},
  ]
}
DERISK_TYPES: dict[str, list[Field]] = {
  'SetDeriskToMaintenanceMarginRatio': [
    {'name': 'subAccountID', 'type': 'uint64'},
    {'name': 'deriskToMaintenanceMarginRatio', 'type': 'uint32'},
    {'name': 'nonce', 'type': 'uint32'},
    {'name': 'expiration', 'type': 'int64'},
  ]
}
POSITION_CONFIG_TYPES: dict[str, list[Field]] = {
  'SetSubAccountPositionMarginConfig': [
    {'name': 'subAccountID', 'type': 'uint64'},
    {'name': 'asset', 'type': 'uint256'},
    {'name': 'marginType', 'type': 'uint8'},
    {'name': 'leverage', 'type': 'int32'},
    {'name': 'nonce', 'type': 'uint32'},
    {'name': 'expiration', 'type': 'int64'},
  ]
}
"""`set_position_config`: the type string of GRVT's exchange contract
(`SubAccountSig.sol`, `_SET_SUB_POSITION_MARGIN_CONFIG_H`)."""
POSITION_MARGIN_TYPES: dict[str, list[Field]] = {
  'AddIsolatedPositionMargin': [
    {'name': 'subAccountID', 'type': 'uint64'},
    {'name': 'asset', 'type': 'uint256'},
    {'name': 'amount', 'type': 'int64'},
    {'name': 'nonce', 'type': 'uint32'},
    {'name': 'expiration', 'type': 'int64'},
  ]
}
"""`add_position_margin`: the type string of GRVT's exchange contract (`TradeSig.sol`,
`_HASH_ADD_ISOLATED_POSITION_MARGIN_H`)."""
WALLET_LOGIN_TYPES: dict[str, list[Field]] = {
  'WalletLogin': [
    {'name': 'signer', 'type': 'address'},
    {'name': 'nonce', 'type': 'uint32'},
    {'name': 'expiration', 'type': 'int64'},
  ]
}

SIGNED_TIME_IN_FORCE = {
  'GOOD_TILL_TIME': 1,
  'ALL_OR_NONE': 2,
  'IMMEDIATE_OR_CANCEL': 3,
  'FILL_OR_KILL': 4,
  'RETAIL_PRICE_IMPROVEMENT': 5,
}
"""Wire `TimeInForce` -> the `uint8` signed in `Order.timeInForce`: the ordinal of GRVT's
Solidity `enum TimeInForce` (exchange-contract `contracts/exchange/types/Enum.sol`, with
`UNSPECIFIED = 0`), the same numbering as the `TimeInForce` enum of GRVT's published API
spec (`gravity-technologies/api-spec`) and `@grvt/client`'s `ETimeInForceInt`. Kept
explicit rather than derived from the request type's `Literal`, so a type change never
changes the signing encoding."""

SIGNED_MARGIN_TYPE = {'ISOLATED': 1, 'CROSS': 2}
"""Wire `PositionMarginType` -> the `uint8` signed in `marginType`: the ordinal of the exchange
contract's `enum PositionMarginType` (`contracts/exchange/types/Enum.sol`, with
`UNSPECIFIED = 0`), the same values as the `PositionMarginType` enum of GRVT's API spec."""

PRICE_DECIMALS = 9
"""`OrderLeg.limitPrice` is the price scaled by 1e9."""
BUILDER_FEE_DECIMALS = 4
"""`OrderWithBuilderFee.builderFee` is the fee rate scaled by 1e4."""
DERISK_RATIO_DECIMALS = 6
"""`deriskToMaintenanceMarginRatio` is the ratio scaled by 1e6."""
LEVERAGE_DECIMALS = 6
"""`SetSubAccountPositionMarginConfig.leverage` is the leverage scaled by 1e6 (the exchange
contract caps it at `50_000_000`, "50x")."""
ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'

LOGIN_TTL = timedelta(minutes=4)
"""Wallet-login signature lifetime; the venue rejects anything over 5 minutes ahead."""


class InstrumentKey(TypedDict):
  """The instrument facts an order or position signature needs."""

  instrument_hash: str
  """`OrderLeg.assetID` (and a position's `asset`), as a hex string."""
  base_decimals: int
  """`OrderLeg.contractSize` is the size scaled by `10**base_decimals`."""
  quote: str
  """Quote currency, whose `balance_decimals` scale isolated margin amounts."""


class CurrencyKey(TypedDict):
  """The currency facts a transfer or withdrawal signature needs."""

  id: int
  """`tokenCurrency`."""
  balance_decimals: int
  """`numTokens` is the amount scaled by `10**balance_decimals`."""


class Signature(TypedDict):
  """A GRVT payload signature, in wire format."""

  signer: str
  r: str
  s: str
  v: int
  expiration: str
  """Unix nanoseconds, as a string."""
  nonce: int
  chain_id: str


DIGITS = re.compile(r'-?[0-9]+')
"""An integer in decimal digits, as 64-bit integers are sent on the wire."""
HEX_ADDRESS = re.compile(r'0x[0-9a-fA-F]{40}')
"""A hex EVM address, in any case."""
PLAIN_DECIMAL = re.compile(r'-?[0-9]+(\.[0-9]+)?')
"""A decimal in plain notation (`0.004`, `50000`): the form `typed_core.decimals.plain`
writes a `Decimal` in, and the only form a caller's own decimal string is signed in."""


def bounds(bits: int, *, signed: bool = False) -> tuple[int, int]:
  """The range of a Solidity integer type: `uint<bits>`, or `int<bits>` when `signed`."""
  if signed:
    return -(2 ** (bits - 1)), 2 ** (bits - 1) - 1
  return 0, 2**bits - 1


def integer(value: Any, *, bits: int, what: str, signed: bool = False) -> int:
  """Parse an integer wire value (a JSON number, or a string of decimal digits) that a
  struct field signs, checking that it fits the field.

  Args:
    value: Integer, or decimal digits as sent on the wire.
    bits: Width of the signed field.
    what: Field name, for the error message.
    signed: The field is `int<bits>` rather than `uint<bits>`.

  Raises:
    BadRequest: The value is not an integer, or does not fit the field.
  """
  if isinstance(value, int) and not isinstance(value, bool):
    number = value
  elif isinstance(value, str) and DIGITS.fullmatch(value):
    number = int(value)
  else:
    raise BadRequest(f'{what} must be an integer, got {value!r}')
  low, high = bounds(bits, signed=signed)
  if not low <= number <= high:
    raise BadRequest(f'{what}={value} is out of range: it must be in [{low}, {high}]')
  return number


def scaled(
  value: Any, decimals: int, *, what: str, bits: int = 64, signed: bool = False
) -> int:
  """Scale a decimal wire value to the integer a struct field signs.

  A string must be in plain notation (`PLAIN_DECIMAL`). It reaches the wire untouched, and
  the venue verifies the signature against the value it reads from that string, so a form
  `Decimal` accepts but the venue may read differently (`1E-9`, `1_000`, ` 1.5`) is
  refused rather than signed.

  Args:
    value: Decimal string as sent on the wire (`0.004`, from a `Decimal` or as the caller
      wrote it), or an integer default.
    decimals: Power of ten to scale by.
    what: Field name, for the error message.
    bits: Width of the signed field.
    signed: The field is `int<bits>` rather than `uint<bits>`.

  Raises:
    BadRequest: The value is not a finite decimal, is a string not in plain notation, has
      more precision than `decimals` allows, or is out of the field's range once scaled
      (negative, for an unsigned field).
  """
  try:
    number = Decimal(str(value)) * (Decimal(10) ** decimals)
  except InvalidOperation as e:
    raise BadRequest(f'{what} must be a decimal, got {value!r}') from e
  if not number.is_finite():
    raise BadRequest(f'{what} must be a finite decimal, got {value!r}')
  if isinstance(value, str) and not PLAIN_DECIMAL.fullmatch(value):
    raise BadRequest(
      f'{what} must be a decimal in plain notation (digits, with at most one decimal '
      f'point, like 0.004), got {value!r}'
    )
  if number != number.to_integral_value():
    raise BadRequest(f'{what}={value} has more than {decimals} decimals')
  low, high = bounds(bits, signed=signed)
  if not low <= number <= high:
    lowest = plain(Decimal(low).scaleb(-decimals))
    largest = plain(Decimal(high).scaleb(-decimals))
    raise BadRequest(
      f'{what}={value} is out of range: it must be in [{lowest}, {largest}]'
    )
  return int(number)


def address(value: Any, *, what: str) -> str:
  """Check an address wire value that a struct field signs.

  Args:
    value: Hex address, as sent on the wire.
    what: Field name, for the error message.

  Raises:
    BadRequest: The value is not a `0x`-prefixed 20-byte hex address.
  """
  if not isinstance(value, str) or not HEX_ADDRESS.fullmatch(value):
    raise BadRequest(f'{what} must be a 0x-prefixed 20-byte hex address, got {value!r}')
  return value


def has_builder(order: Mapping[str, Any]) -> bool:
  """Whether an order names a non-zero builder, switching it to `OrderWithBuilderFee`."""
  builder = order.get('builder')
  return bool(builder) and builder not in ('0', ZERO_ADDRESS)


@dataclass(frozen=True)
class Signer:
  """The EIP-712 signer of one GRVT environment: an API key's signer key, or a wallet."""

  account: LocalAccount
  chain_id: int
  """GRVT L2 chain id of the environment this signer signs for."""

  @classmethod
  def from_key(cls, private_key: str, *, chain_id: int) -> 'Signer':
    """Build a signer from a hex private key.

    Args:
      private_key: Hex private key, with or without `0x`.
      chain_id: GRVT L2 chain id of the target environment.

    Raises:
      AuthError: `private_key` is not a valid private key. The message never includes
        the key, and the underlying error (which might) is not chained.
    """
    try:
      account = Account.from_key(private_key)
    except Exception:
      raise AuthError(
        'Invalid private key: expected a 32-byte secp256k1 key as 64 hex digits, with or '
        'without 0x'
      ) from None
    return cls(account, chain_id)

  @property
  def address(self) -> str:
    """The signer's checksummed address."""
    return self.account.address

  def sign(
    self,
    types: Mapping[str, list[Field]],
    message: Mapping[str, Any],
    *,
    nonce: int,
    expiration: int,
  ) -> Signature:
    """Sign one struct (its primary type is the first key of `types`).

    Args:
      types: EIP-712 struct types, primary type first, `EIP712Domain` excluded.
      message: Struct values, without `nonce`/`expiration`.
      nonce: Random `uint32`, the venue's replay key.
      expiration: Unix nanoseconds after which the signature is void.
    """
    domain = {'name': 'GRVT Exchange', 'version': '0', 'chainId': self.chain_id}
    full = {**message, 'nonce': nonce, 'expiration': expiration}
    signed = self.account.sign_message(encode_typed_data(domain, dict(types), full))
    return {
      'signer': self.address,
      'r': '0x' + signed.r.to_bytes(32, 'big').hex(),
      's': '0x' + signed.s.to_bytes(32, 'big').hex(),
      'v': signed.v,
      'expiration': str(expiration),
      'nonce': nonce,
      'chain_id': str(self.chain_id),
    }

  def sign_payload(
    self,
    types: Mapping[str, list[Field]],
    *,
    message: Mapping[str, Any],
    payload: Mapping[str, Any],
    ttl: timedelta,
  ) -> dict[str, Any]:
    """Return a copy of `payload` with its `signature` filled in.

    A `nonce`/`expiration` already present in `payload['signature']` is kept, so a caller
    can pin either; anything else is generated (random nonce, `now + ttl`).

    Args:
      types: EIP-712 struct types, primary type first.
      message: Struct values derived from `payload`, without `nonce`/`expiration`.
      payload: Wire payload carrying the signature.
      ttl: Signature lifetime when `payload` pins no expiration.

    Raises:
      BadRequest: A pinned nonce is not a `uint32`, or a pinned expiration not an `int64`.
    """
    given = payload.get('signature') or {}
    nonce = integer(
      given.get('nonce') or secrets.randbits(32) or 1, bits=32, what='signature.nonce'
    )
    expiration = integer(
      given.get('expiration') or time.time_ns() + int(ttl.total_seconds() * 1e9),
      bits=64,
      signed=True,
      what='signature.expiration',
    )
    signature = self.sign(types, message, nonce=nonce, expiration=expiration)
    return {**payload, 'signature': signature}

  def order(
    self,
    order: Mapping[str, Any],
    instruments: Mapping[str, InstrumentKey],
    *,
    ttl: timedelta,
  ) -> dict[str, Any]:
    """Sign an `Order` (or `OrderWithBuilderFee` when it names a builder).

    Args:
      order: Wire `Order`.
      instruments: Signing facts of every instrument the order's legs trade.
      ttl: Signature lifetime when the order pins no expiration.

    Raises:
      BadRequest: An unknown or missing time in force; a leg size with more decimals than
        its instrument's `base_decimals`, or a limit price with more than 9 decimals (the
        precision each is signed with; neither is checked against the instrument's
        `tick_size` or `min_size`); a size or price that is negative or too large to sign;
        a `sub_account_id` that is not a `uint64`; or a malformed builder address or fee.
    """
    tif = order.get('time_in_force')
    if tif not in SIGNED_TIME_IN_FORCE:
      raise BadRequest(f'Unknown time_in_force {tif!r}')
    legs = []
    for leg in order.get('legs', []):
      instrument = instruments[leg['instrument']]
      legs.append(
        {
          'assetID': int(instrument['instrument_hash'], 16),
          'contractSize': scaled(leg['size'], instrument['base_decimals'], what='size'),
          'limitPrice': scaled(
            leg.get('limit_price', 0), PRICE_DECIMALS, what='limit_price'
          ),
          'isBuyingContract': bool(leg['is_buying_asset']),
        }
      )
    message: dict[str, Any] = {
      'subAccountID': integer(
        order.get('sub_account_id'), bits=64, what='sub_account_id'
      ),
      'isMarket': bool(order.get('is_market')),
      'timeInForce': SIGNED_TIME_IN_FORCE[tif],
      'postOnly': bool(order.get('post_only')),
      'reduceOnly': bool(order.get('reduce_only')),
      'legs': legs,
    }
    types = ORDER_TYPES
    if has_builder(order):
      types = ORDER_WITH_BUILDER_FEE_TYPES
      message['builder'] = address(order['builder'], what='builder')
      message['builderFee'] = scaled(
        order.get('builder_fee', 0), BUILDER_FEE_DECIMALS, what='builder_fee', bits=32
      )
    return self.sign_payload(types, message=message, payload=order, ttl=ttl)

  def transfer(
    self, transfer: Mapping[str, Any], currency: CurrencyKey, *, ttl: timedelta
  ) -> dict[str, Any]:
    """Sign a `Transfer` between accounts or sub-accounts.

    Args:
      transfer: Wire `ApiTransferRequest`.
      currency: Signing facts of the transferred currency.
      ttl: Signature lifetime when the transfer pins no expiration.

    Raises:
      BadRequest: A malformed account address, a sub-account id that is not a `uint64`,
        or an amount finer than the currency allows, negative, or too large to sign.
    """
    message = {
      'fromAccount': address(transfer.get('from_account_id'), what='from_account_id'),
      'fromSubAccount': integer(
        transfer.get('from_sub_account_id') or 0, bits=64, what='from_sub_account_id'
      ),
      'toAccount': address(transfer.get('to_account_id'), what='to_account_id'),
      'toSubAccount': integer(
        transfer.get('to_sub_account_id') or 0, bits=64, what='to_sub_account_id'
      ),
      'tokenCurrency': currency['id'],
      'numTokens': scaled(
        transfer.get('num_tokens'), currency['balance_decimals'], what='num_tokens'
      ),
    }
    return self.sign_payload(TRANSFER_TYPES, message=message, payload=transfer, ttl=ttl)

  def withdrawal(
    self, withdrawal: Mapping[str, Any], currency: CurrencyKey, *, ttl: timedelta
  ) -> dict[str, Any]:
    """Sign a `Withdrawal` to an Ethereum address.

    Args:
      withdrawal: Wire `ApiWithdrawalRequest`.
      currency: Signing facts of the withdrawn currency.
      ttl: Signature lifetime when the withdrawal pins no expiration.

    Raises:
      BadRequest: A malformed address, or an amount finer than the currency allows,
        negative, or too large to sign.
    """
    message = {
      'fromAccount': address(withdrawal.get('from_account_id'), what='from_account_id'),
      'toEthAddress': address(withdrawal.get('to_eth_address'), what='to_eth_address'),
      'tokenCurrency': currency['id'],
      'numTokens': scaled(
        withdrawal.get('num_tokens'), currency['balance_decimals'], what='num_tokens'
      ),
    }
    return self.sign_payload(
      WITHDRAWAL_TYPES, message=message, payload=withdrawal, ttl=ttl
    )

  def derisk(self, request: Mapping[str, Any], *, ttl: timedelta) -> dict[str, Any]:
    """Sign a `SetDeriskToMaintenanceMarginRatio` request.

    Args:
      request: Wire `ApiSetDeriskToMaintenanceMarginRatioRequest`.
      ttl: Signature lifetime when the request pins no expiration.

    Raises:
      BadRequest: A `sub_account_id` that is not a `uint64`, or a ratio finer than 1e-6,
        negative, or too large to sign.
    """
    message = {
      'subAccountID': integer(
        request.get('sub_account_id'), bits=64, what='sub_account_id'
      ),
      'deriskToMaintenanceMarginRatio': scaled(
        request.get('ratio'), DERISK_RATIO_DECIMALS, what='ratio', bits=32
      ),
    }
    return self.sign_payload(DERISK_TYPES, message=message, payload=request, ttl=ttl)

  def position_config(
    self, request: Mapping[str, Any], instrument: InstrumentKey, *, ttl: timedelta
  ) -> dict[str, Any]:
    """Sign a `SetSubAccountPositionMarginConfig` request (`set_position_config`).

    Args:
      request: Wire `ApiSetSubAccountPositionMarginConfigRequest`.
      instrument: Signing facts of the request's instrument.
      ttl: Signature lifetime when the request pins no expiration.

    Raises:
      BadRequest: An unknown margin type, a `sub_account_id` that is not a `uint64`, or a
        leverage finer than 1e-6, negative, or too large to sign.
    """
    margin_type = request.get('margin_type')
    if margin_type not in SIGNED_MARGIN_TYPE:
      raise BadRequest(f'Unknown margin_type {margin_type!r}')
    # `leverage` is an `int32`; `bits=31` unsigned is its non-negative half.
    message = {
      'subAccountID': integer(
        request.get('sub_account_id'), bits=64, what='sub_account_id'
      ),
      'asset': int(instrument['instrument_hash'], 16),
      'marginType': SIGNED_MARGIN_TYPE[margin_type],
      'leverage': scaled(
        request.get('leverage'), LEVERAGE_DECIMALS, what='leverage', bits=31
      ),
    }
    return self.sign_payload(
      POSITION_CONFIG_TYPES, message=message, payload=request, ttl=ttl
    )

  def position_margin(
    self,
    request: Mapping[str, Any],
    instrument: InstrumentKey,
    quote: CurrencyKey,
    *,
    ttl: timedelta,
  ) -> dict[str, Any]:
    """Sign an `AddIsolatedPositionMargin` request (`add_position_margin`).

    Args:
      request: Wire `ApiAddIsolatedPositionMarginRequest`.
      instrument: Signing facts of the request's instrument.
      quote: Signing facts of the instrument's quote currency, which the amount is in.
      ttl: Signature lifetime when the request pins no expiration.

    Raises:
      BadRequest: A `sub_account_id` that is not a `uint64`, or an amount finer than the
        quote currency allows or too large to sign. A negative amount (removing margin) is
        signed as is.
    """
    message = {
      'subAccountID': integer(
        request.get('sub_account_id'), bits=64, what='sub_account_id'
      ),
      'asset': int(instrument['instrument_hash'], 16),
      'amount': scaled(
        request.get('amount'),
        quote['balance_decimals'],
        what='amount',
        signed=True,
      ),
    }
    return self.sign_payload(
      POSITION_MARGIN_TYPES, message=message, payload=request, ttl=ttl
    )

  def wallet_login(self) -> Signature:
    """Sign a `WalletLogin`, valid for `LOGIN_TTL` (the venue allows at most 5 minutes)."""
    expiration = time.time_ns() + int(LOGIN_TTL.total_seconds() * 1e9)
    nonce = secrets.randbits(32) or 1
    return self.sign(
      WALLET_LOGIN_TYPES, {'signer': self.address}, nonce=nonce, expiration=expiration
    )
