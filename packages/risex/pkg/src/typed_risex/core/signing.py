"""Signing RISEx calls: completing a request body with the signatures and nonces it needs.

An endpoint declares what its body needs signed (`Meta.sign`), and the caller passes only
the action's own fields; `Signing.attach` fills in the rest. Three shapes exist:

- **permits** (`place_order`, `cancel_order`, `cancel_all_orders`, `approve_builder_fee`,
  `update_leverage`, `update_margin_mode`, `update_isolated_margin`): the signer key signs a
  `VerifyWitness` over the action hash, attached as `permit` (`permit_params` on the three
  account endpoints);
- **account setup** (`register_signer`, `revoke_signer`, `approve_single`): the account key
  signs a struct of its own (and, to register, the signer key countersigns), flattened into
  the body as `0x`-hex signatures;
- **login**: an EIP-712 `Login` over a one-time server nonce, signed by the account key, or
  by the signer key on the account's behalf when only that one is configured.

The domain, router and OperatorHub addresses are fetched from the API on first use and
cached for the client's life; the nonce state is loaded once per session (`core.nonces`).
"""

from typing_extensions import (
  Any,
  Literal,
  Mapping,
  Protocol,
  TypedDict,
  TypeIs,
  get_args,
)
from dataclasses import dataclass, field
import asyncio
import time

from eth_utils.address import to_checksum_address

from typed_core.validation import validator

from . import eip712
from .auth import Credentials
from .eip712 import Domain
from .exc import AuthError, BadRequest, LogicError
from .networks import NetworkProfile
from .nonces import Nonces

PermitKind = Literal[
  'place_order',
  'cancel_order',
  'cancel_all_orders',
  'approve_builder_fee',
  'update_leverage',
  'update_margin_mode',
  'update_isolated_margin',
]
"""Actions authorized by a signer permit."""

SetupKind = Literal['register_signer', 'revoke_signer', 'approve_single']
"""Actions signed by the account key, with an account nonce."""

SignKind = PermitKind | SetupKind | Literal['login']
"""Everything `Signing.attach` can sign."""

PERMIT_FIELD: dict[PermitKind, Literal['permit', 'permit_params']] = {
  'place_order': 'permit',
  'cancel_order': 'permit',
  'cancel_all_orders': 'permit',
  'approve_builder_fee': 'permit',
  'update_leverage': 'permit_params',
  'update_margin_mode': 'permit_params',
  'update_isolated_margin': 'permit_params',
}
"""Body field each permit is attached as."""


def is_permit(kind: SignKind) -> TypeIs[PermitKind]:
  """Whether `kind` is authorized by a signer permit."""
  return kind in get_args(PermitKind)


PERMIT_TTL = 300
"""Seconds a permit or login signature stays valid (`deadline`)."""

SIGNER_TTL = 30 * 86400
"""Default lifetime of a signer registration, in seconds, when the call sets no
`expiration`."""

DEFAULT_SIGNER_MESSAGE = 'RISEx session key'
"""Default `message` of a signer registration."""


class Api(Protocol):
  """What signing needs from the REST transport: one unsigned, unvalidated call."""

  async def call(
    self,
    method: str,
    path: str,
    *,
    params: Mapping[str, Any] | None = None,
    json: Any | None = None,
  ) -> Any:
    """Send one unauthenticated request and return its unwrapped `data`."""
    ...


class DomainWire(TypedDict):
  """`GET /v1/auth/eip712-domain` payload."""

  name: str
  version: str
  chain_id: str
  verifying_contract: str


class AddressesWire(TypedDict):
  """The contract addresses signing needs, from `GET /v1/system/config`."""

  router: str
  auth: str
  operator_hub: str


class ConfigWire(TypedDict):
  """`GET /v1/system/config` payload, as signing reads it."""

  addresses: AddressesWire


class NonceStateWire(TypedDict):
  """`GET /v1/nonce-state/{account}` payload."""

  nonce_anchor: str
  current_bitmap_index: int


class LoginNonceWire(TypedDict):
  """`GET /v1/auth/nonce` payload."""

  nonce: str


class Permit(TypedDict):
  """A signed permit, as sent in `permit`/`permit_params`."""

  account: str
  signer: str
  nonce_anchor: str
  nonce_bitmap_index: int
  deadline: int
  signature: str
  """Base64 of the 64-byte EIP-2098 compact signature."""


@dataclass(frozen=True, kw_only=True)
class Contracts:
  """Contract addresses signatures commit to."""

  router: str
  """`RISExUniversalRouter`: every permit's `target`."""
  operator_hub: str
  """`OperatorHub`: the default `operator` of an allowance."""


def integer(values: Mapping[str, Any], name: str, default: int | None = None) -> int:
  """Read an integer body field, sent as a number or a numeral string.

  Raises:
    BadRequest: The field is missing (with no default) or not an integer.
  """
  value = values.get(name)
  if value is None or value == '':
    if default is None:
      raise BadRequest(f'Missing `{name}`')
    return default
  if isinstance(value, bool):
    return int(value)
  try:
    return int(value)
  except (TypeError, ValueError):
    raise BadRequest(f'`{name}` must be an integer, got {value!r}') from None


def permit_hash(kind: PermitKind, values: Mapping[str, Any]) -> bytes:
  """The action hash a permit for `kind` commits to, from the request's own fields.

  Raises:
    BadRequest: A field the hash needs is missing or malformed.
  """
  if kind == 'place_order':
    order_data = eip712.pack_order(
      market_id=integer(values, 'market_id'),
      size_steps=integer(values, 'size_steps'),
      price_ticks=integer(values, 'price_ticks'),
      side=integer(values, 'side'),
      post_only=bool(values.get('post_only', False)),
      reduce_only=bool(values.get('reduce_only', False)),
      stp_mode=integer(values, 'stp_mode', 0),
      order_type=integer(values, 'order_type'),
      time_in_force=integer(values, 'time_in_force', 0),
    )
    return eip712.place_order_hash(
      order_data,
      builder_id=integer(values, 'builder_id', 0),
      builder_fee_bps=integer(values, 'builder_fee_bps', 0),
      client_order_id=integer(values, 'client_order_id', 0),
      ttl_units=integer(values, 'ttl_units', 0),
    )
  if kind == 'cancel_order':
    order_id = values.get('order_id')
    if not isinstance(order_id, str):
      raise BadRequest('Missing `order_id`')
    return eip712.action_hash(
      'RISE_PERPS_CANCEL_ORDER_V1',
      ['uint256', 'uint256'],
      [integer(values, 'market_id'), eip712.resting_order_id(order_id)],
    )
  if kind == 'cancel_all_orders':
    return eip712.action_hash(
      'RISE_PERPS_CANCEL_ALL_ORDERS_V1', ['uint256'], [integer(values, 'market_id')]
    )
  if kind == 'approve_builder_fee':
    return eip712.action_hash(
      'RISE_APPROVE_BUILDER_FEE_V1',
      ['uint16', 'uint16'],
      [integer(values, 'builder_id'), integer(values, 'max_fee_bps')],
    )
  if kind == 'update_leverage':
    return eip712.action_hash(
      'RISE_PERPS_UPDATE_LEVERAGE_V1',
      ['uint16', 'uint8'],
      [integer(values, 'market_id'), integer(values, 'leverage')],
    )
  if kind == 'update_margin_mode':
    return eip712.action_hash(
      'RISE_PERPS_UPDATE_MARGIN_MODE_V1',
      ['uint16', 'uint8'],
      [integer(values, 'market_id'), integer(values, 'margin_mode')],
    )
  return eip712.action_hash(
    'RISE_PERPS_UPDATE_ISOLATED_MARGIN_V1',
    ['uint16', 'int128'],
    [integer(values, 'market_id'), integer(values, 'amount')],
  )


@dataclass(kw_only=True)
class Signing:
  """Signing state of one client: its credentials, the cached domain and contracts, and
  the account's nonces.
  """

  network: NetworkProfile
  """Deployment the client talks to; the fetched domain must name its chain."""
  credentials: Credentials | None
  """Keys to sign with; `None` for a public client."""
  nonces: Nonces = field(default_factory=Nonces)
  """The account's anchor + bitmap nonce state."""
  domain_cache: Domain | None = field(default=None, init=False, repr=False)
  contracts_cache: Contracts | None = field(default=None, init=False, repr=False)
  lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False, repr=False)

  def require_credentials(self) -> Credentials:
    """The credentials, for a signed call.

    Raises:
      AuthError: The client was built with `public=True`.
    """
    if self.credentials is None:
      raise AuthError(
        'This call is signed: build the client with keys, not `public=True`.'
      )
    return self.credentials

  async def domain(self, api: Api) -> Domain:
    """The EIP-712 domain, fetched on first use.

    Raises:
      LogicError: The API's domain names a different chain than the configured network.
    """
    async with self.lock:
      if self.domain_cache is None:
        wire = validator(DomainWire).python(
          await api.call('GET', '/v1/auth/eip712-domain')
        )
        chain_id = int(wire['chain_id'])
        if chain_id != self.network.chain_id:
          raise LogicError(
            f'{self.network.name} API signs for chain {chain_id}, expected '
            f'{self.network.chain_id}: refusing to sign'
          )
        self.domain_cache = {
          'name': wire['name'],
          'version': wire['version'],
          'chainId': chain_id,
          'verifyingContract': to_checksum_address(wire['verifying_contract']),
        }
      return self.domain_cache

  async def contracts(self, api: Api) -> Contracts:
    """The router and OperatorHub addresses, fetched on first use."""
    async with self.lock:
      if self.contracts_cache is None:
        wire = validator(ConfigWire).python(await api.call('GET', '/v1/system/config'))
        addresses = wire['addresses']
        self.contracts_cache = Contracts(
          router=to_checksum_address(addresses['router']),
          operator_hub=to_checksum_address(addresses['operator_hub']),
        )
      return self.contracts_cache

  async def nonce(self, api: Api, account: str) -> tuple[int, int]:
    """The next `(anchor, bit)` pair for `account`."""

    async def load() -> int:
      """The account's current anchor."""
      wire = await api.call('GET', f'/v1/nonce-state/{account}')
      return int(validator(NonceStateWire).python(wire)['nonce_anchor'])

    return await self.nonces.take(load)

  async def permit(self, api: Api, action_hash: bytes) -> Permit:
    """Sign one `VerifyWitness` permit over `action_hash` with the signer key.

    Raises:
      AuthError: No signer key is configured.
    """
    credentials = self.require_credentials()
    key = credentials.require_signer_key()
    domain = await self.domain(api)
    contracts = await self.contracts(api)
    anchor, bit = await self.nonce(api, credentials.account)
    deadline = int(time.time()) + PERMIT_TTL
    signature, v = eip712.sign_struct(
      key,
      domain,
      'VerifyWitness',
      {
        'account': credentials.account,
        'target': contracts.router,
        'hash': action_hash,
        'nonceAnchor': anchor,
        'nonceBitmap': bit,
        'deadline': deadline,
      },
    )
    return {
      'account': credentials.account,
      'signer': key.address,
      'nonce_anchor': str(anchor),
      'nonce_bitmap_index': bit,
      'deadline': deadline,
      'signature': eip712.compact_signature(signature, v),
    }

  async def attach(
    self, api: Api, kind: SignKind, values: dict[str, Any]
  ) -> dict[str, Any]:
    """Complete a request body for `kind`: compute and attach its signatures, nonces and
    the signing identities, leaving the action's own fields as the caller set them.

    Args:
      api: The REST transport, for the domain, contracts and nonce state.
      kind: What the body authorizes.
      values: The body's fields, as the caller set them.

    Raises:
      AuthError: The key this call needs is not configured.
      BadRequest: A field the signature commits to is missing or malformed.
    """
    if is_permit(kind):
      action_hash = permit_hash(kind, values)
      return {**values, PERMIT_FIELD[kind]: await self.permit(api, action_hash)}
    if kind == 'login':
      return await self.login(api)
    return await self.setup(api, kind, values)

  async def setup(
    self, api: Api, kind: SetupKind, values: dict[str, Any]
  ) -> dict[str, Any]:
    """Sign an account setup action (see `attach`)."""
    credentials = self.require_credentials()
    account_key = credentials.require_account_key()
    domain = await self.domain(api)
    anchor, bit = await self.nonce(api, credentials.account)
    nonce = {'nonceAnchor': anchor, 'nonceBitmap': bit}
    body = {
      **values,
      'account': credentials.account,
      'nonce_anchor': str(anchor),
      'nonce_bitmap_index': bit,
    }
    if kind == 'register_signer':
      signer_key = credentials.require_signer_key()
      message = values.get('message') or DEFAULT_SIGNER_MESSAGE
      expiration = integer(values, 'expiration', int(time.time()) + SIGNER_TTL)
      account_signature, _ = eip712.sign_struct(
        account_key,
        domain,
        'RegisterSigner',
        {
          'account': credentials.account,
          'signer': signer_key.address,
          'message': message,
          'expiration': expiration,
          **nonce,
        },
      )
      signer_signature, _ = eip712.sign_struct(
        signer_key, domain, 'VerifySigner', {'account': credentials.account, **nonce}
      )
      return {
        **body,
        'signer': signer_key.address,
        'message': message,
        'expiration': str(expiration),
        'account_signature': eip712.hex_signature(account_signature),
        'signer_signature': eip712.hex_signature(signer_signature),
      }
    if kind == 'revoke_signer':
      signer = values.get('signer') or credentials.signer
      if not signer:
        raise BadRequest('Missing `signer`: name the signer to revoke')
      signer = to_checksum_address(signer)
      signature, _ = eip712.sign_struct(
        account_key,
        domain,
        'RevokeSigner',
        {'account': credentials.account, 'signer': signer, **nonce},
      )
      return {
        **body,
        'signer': signer,
        'account_signature': eip712.hex_signature(signature),
      }
    operator = values.get('operator') or (await self.contracts(api)).operator_hub
    operator = to_checksum_address(operator)
    budget = integer(values, 'budget')
    expiry = integer(values, 'allowance_expiry')
    signature, _ = eip712.sign_struct(
      account_key,
      domain,
      'PermitSingle',
      {
        'account': credentials.account,
        'operator': operator,
        'budget': budget,
        'allowanceExpiry': expiry,
        **nonce,
      },
    )
    return {
      **body,
      'operator': operator,
      'budget': str(budget),
      'allowance_expiry': expiry,
      'signature': eip712.hex_signature(signature),
    }

  async def login(self, api: Api) -> dict[str, Any]:
    """A `POST /v1/auth/login` body over a fresh server nonce.

    Signed by the account key when configured; otherwise by the signer key, naming itself
    as `signer`.

    Raises:
      AuthError: No key is configured.
    """
    credentials = self.require_credentials()
    domain = await self.domain(api)
    nonce = validator(LoginNonceWire).python(await api.call('GET', '/v1/auth/nonce'))[
      'nonce'
    ]
    deadline = int(time.time()) + PERMIT_TTL
    key = credentials.account_key or credentials.require_signer_key()
    signature, _ = eip712.sign_struct(
      key,
      domain,
      'Login',
      {'account': credentials.account, 'nonce': int(nonce, 16), 'deadline': deadline},
    )
    body: dict[str, Any] = {
      'account': credentials.account,
      'nonce': nonce,
      'deadline': deadline,
      'signature': eip712.hex_signature(signature),
    }
    if credentials.account_key is None:
      body['signer'] = key.address
    return body

  async def ws_auth(self, api: Api, message: str) -> dict[str, Any]:
    """`auth_v2` params for the WebSocket: a `RegisterV2` over a fresh server nonce,
    signed by the signer key.

    Raises:
      AuthError: No signer key is configured.
    """
    credentials = self.require_credentials()
    key = credentials.require_signer_key()
    domain = await self.domain(api)
    nonce = validator(LoginNonceWire).python(await api.call('GET', '/v1/auth/nonce'))[
      'nonce'
    ]
    signature, _ = eip712.sign_struct(
      key,
      domain,
      'RegisterV2',
      {'signer': key.address, 'message': message, 'nonce': int(nonce, 16)},
    )
    return {
      'account': credentials.account,
      'signer': key.address,
      'message': message,
      'nonce': nonce,
      'signature': eip712.hex_signature(signature),
    }
