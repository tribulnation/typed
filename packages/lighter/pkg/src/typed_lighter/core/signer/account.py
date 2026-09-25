"""`AccountSigner`: the `client.signer` surface, every API key of one account on one network.

Local only: every method validates, signs and returns a `SignedTx`, with no network call and
no nonce bookkeeping. There is one sign twin per `client.tx` transaction, taking an explicit
`nonce`, for callers who pre-sign, batch, or manage nonces themselves; `client.tx` signs
through these same methods.

Every twin also takes:

- `nonce`: the API key's nonce (`GET /api/v1/nextNonce`).
- `api_key_index`: the slot to sign with; the first configured one by default.
- `skip_nonce`: accept any increasing nonce instead of exactly the next one.
- `expires_at`: when the sequencer stops accepting the transaction; 10 minutes (minus a
  second) from now by default, as lighter-go does.

Every signed time (`expires_at`, `order_expiry`, `cancel_at`, `approval_expiry`, an auth
token's expiry) must be a timezone-aware `datetime`: a naive one raises `BadRequest`,
since a signature commits to the value and a local-time guess would be silently hours off.
"""

from typing_extensions import (
  TYPE_CHECKING,
  Iterator,
  Literal,
  Mapping,
  TypeAlias,
  TypedDict,
  TypeVar,
)
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from ..exc import AuthError, BadRequest
from ..types import timestamp_millis
from .key import ApiKeyPair, PythonSigner, Signer, generate_api_key
from .l1 import eth_sign
from .token import auth_token, aware
from .txs.account import (
  ApproveIntegrator,
  ChangePubKey,
  CreateSubAccount,
  UpdateAccountAssetConfig,
  UpdateAccountConfig,
  UpdateLeverage,
  UpdateMargin,
)
from .txs.assets import StakeAssets, Transfer, UnstakeAssets, Withdraw
from .txs.base import Attributes, L2Tx, SignedTx
from .txs.orders import (
  CancelAllOrders,
  CancelOrder,
  CreateGroupedOrders,
  CreateOrder,
  ModifyOrder,
  OrderInfo,
)
from .txs.pools import BurnShares, CreatePublicPool, MintShares, UpdatePublicPool

if TYPE_CHECKING:
  # The twins take exactly the shapes `client.tx` takes, typed with the generated request
  # types. Those modules import this one (through `tx.core`), so the import is for type
  # checking only; at runtime a twin only reads the mapping.
  from ...tx.approve_integrator import IntegratorApproval, IntegratorRevocation
  from ...tx.cancel_all_orders import (
    AbortScheduledCancelAll,
    CancelAllNow,
    ScheduleCancelAll,
  )
  from ...schemas import GroupPrimaryOrder, StopLossLeg, TakeProfitLeg
  from ...tx.create_grouped_orders import OcoGroup, OtocoGroup, OtoGroup, OtoTrigger
  from ...tx.create_order import (
    IocLimitOrder,
    LimitOrder,
    MarketOrder,
    StopLossLimitOrder,
    StopLossOrder,
    TakeProfitLimitOrder,
    TakeProfitOrder,
  )

  NewOrder: TypeAlias = (
    LimitOrder
    | IocLimitOrder
    | MarketOrder
    | StopLossOrder
    | StopLossLimitOrder
    | TakeProfitOrder
    | TakeProfitLimitOrder
  )
  """`client.tx.create_order`'s `order`."""
  OrderGroup: TypeAlias = OtoGroup | OcoGroup | OtocoGroup
  """`client.tx.create_grouped_orders`' `group`."""
  CancelAll: TypeAlias = CancelAllNow | ScheduleCancelAll | AbortScheduledCancelAll
  """`client.tx.cancel_all_orders`' `cancel`."""
  IntegratorApprovalChange: TypeAlias = IntegratorApproval | IntegratorRevocation
  """`client.tx.approve_integrator`'s `approval`."""
  GroupLeg: TypeAlias = StopLossLeg | TakeProfitLeg | OtoTrigger
  """A grouped order's stop-loss or take-profit child."""

OrderType = Literal[
  'limit',
  'market',
  'stop-loss',
  'stop-loss-limit',
  'take-profit',
  'take-profit-limit',
  'twap',
]
"""Order type, spelled as the REST and WS order payloads spell it."""
TimeInForce = Literal['immediate-or-cancel', 'good-till-time', 'post-only']
"""Order time in force, spelled as the REST and WS order payloads spell it."""
SelfTradeBehavior = Literal['expire-maker', 'expire-taker', 'expire-both', 'reduce']
"""What happens when an order would match another order of the same owner."""
SelfTradeEquality = Literal['account', 'master']
"""Whether "same owner" means the same account or the same master account."""
GroupingType = Literal['oto', 'oco', 'otoco']
"""How a group's orders relate: one-triggers-the-other, one-cancels-the-other, or an OTO whose
children are an OCO pair."""
Route = Literal['perps', 'spot']
"""Which side of an account an asset moves from or to."""
MarginMode = Literal['cross', 'isolated']
"""A market's position margin mode."""
MarginDirection = Literal['add', 'remove']
"""Whether USDC moves into or out of an isolated position."""
AccountTradingMode = Literal['classic', 'unified']
"""Classic margin, or the unified trading account (UTA)."""
PoolStatus = Literal['active', 'frozen']
"""A public pool's status."""

K = TypeVar('K')
V = TypeVar('V')

ORDER_TYPES: dict[OrderType, int] = {
  'limit': 0,
  'market': 1,
  'stop-loss': 2,
  'stop-loss-limit': 3,
  'take-profit': 4,
  'take-profit-limit': 5,
  'twap': 6,
}
TIME_IN_FORCE: dict[TimeInForce, int] = {
  'immediate-or-cancel': 0,
  'good-till-time': 1,
  'post-only': 2,
}
IMPLIED_TIME_IN_FORCE: dict[OrderType, TimeInForce] = {
  'limit': 'good-till-time',
  'market': 'immediate-or-cancel',
  'stop-loss': 'immediate-or-cancel',
  'take-profit': 'immediate-or-cancel',
  'stop-loss-limit': 'good-till-time',
  'take-profit-limit': 'good-till-time',
  'twap': 'good-till-time',
}
"""Time in force each order type gets when the caller picks none."""
SELF_TRADE_BEHAVIOR: dict[SelfTradeBehavior, int] = {
  'expire-maker': 0,
  'expire-taker': 1,
  'expire-both': 2,
  'reduce': 3,
}
SELF_TRADE_EQUALITY: dict[SelfTradeEquality, int] = {'account': 0, 'master': 1}
GROUPING_TYPES: dict[GroupingType, int] = {
  'oto': 1,
  'oco': 2,
  'otoco': 3,
}
ACCOUNT_TRADING_MODES: dict[AccountTradingMode, int] = {'classic': 0, 'unified': 1}
POOL_STATUSES: dict[PoolStatus, int] = {'active': 0, 'frozen': 1}
ROUTES: dict[Route, int] = {'perps': 0, 'spot': 1}
MARGIN_MODES: dict[MarginMode, int] = {'cross': 0, 'isolated': 1}
CancelAllMode = Literal['immediate', 'scheduled', 'abort']
"""Cancel now, at a scheduled time, or abort the scheduled cancel-all."""
CANCEL_ALL_MODES: dict[CancelAllMode, int] = {
  'immediate': 0,
  'scheduled': 1,
  'abort': 2,
}

DEFAULT_TX_LIFETIME = timedelta(minutes=10) - timedelta(seconds=1)
"""lighter-go's `DefaultExpireTime`: a transaction's default `expires_at`, from now."""
DEFAULT_ORDER_LIFETIME = timedelta(days=28)
"""The venue's default resting-order lifetime (the shared library's `-1` expiry)."""
MAX_AUTH_TOKEN_LIFETIME = timedelta(hours=8)
"""Furthest ahead the venue accepts a standard auth token's expiry, checked on every request."""


def choose(table: Mapping[K, V], value: K, name: str) -> V:
  """`table[value]` for a closed-set argument.

  Raises:
    BadRequest: `value` is not one of the table's keys.
  """
  try:
    return table[value]
  except (KeyError, TypeError):
    choices = ', '.join(map(repr, table))
    raise BadRequest(f'{name} must be one of {choices}, got {value!r}') from None


@contextmanager
def reading(what: str) -> Iterator[None]:
  """Report a missing key of a caller's mapping as `BadRequest`, not `KeyError`."""
  try:
    yield
  except KeyError as e:
    raise BadRequest(f'{what} is missing {e.args[0]!r}') from None


class Integrator(TypedDict):
  """An integrator charging fees on an order (it must have approved them: `approve_integrator`)."""

  account_index: int
  """Integrator account."""
  taker_fee: int
  """Taker fee in 1e-6 units, at most 1_000_000."""
  maker_fee: int
  """Maker fee in 1e-6 units, at most 1_000_000."""


class BaseFields(TypedDict):
  """The fields every transaction carries."""

  account_index: int
  """Signing account."""
  api_key_index: int
  """API key slot that signs."""
  nonce: int
  """Nonce of that slot."""
  expired_at: int
  """Epoch milliseconds after which the sequencer rejects the transaction."""


def hex_bytes(value: str) -> bytes:
  """Hex (`0x` optional) as bytes; empty on malformed input, which validation then rejects."""
  try:
    return bytes.fromhex(value.removeprefix('0x'))
  except ValueError:
    return b''


def epoch_millis(value: datetime, name: str = 'A signed time') -> int:
  """A timezone-aware datetime as epoch milliseconds.

  Raises:
    BadRequest: `value` is naive.
  """
  return timestamp_millis.dump(aware(value, name))


def order_info(
  *,
  market_index: int,
  client_order_index: int,
  base_amount: int,
  price: int,
  is_ask: bool,
  order_type: OrderType,
  time_in_force: TimeInForce | None,
  reduce_only: bool,
  trigger_price: int,
  order_expiry: datetime | None,
  default_expiry: int,
) -> OrderInfo:
  """The wire `OrderInfo` of one order, with the venue's implied defaults filled in.

  An immediate-or-cancel limit or market order never expires (0), as the venue requires;
  every other order without an explicit expiry expires `default_expiry` (the shared
  library's "28 days" `-1`, computed here from the clock so every order of one group gets
  the same value).

  Raises:
    BadRequest: An immediate-or-cancel limit or market order was given an `order_expiry`,
      which the venue would reject (`OrderExpiry is invalid`).
  """
  tif = time_in_force or choose(IMPLIED_TIME_IN_FORCE, order_type, 'order_type')
  immediate = tif == 'immediate-or-cancel' and order_type in ('limit', 'market')
  if immediate:
    if order_expiry is not None and epoch_millis(order_expiry, 'order_expiry') != 0:
      raise BadRequest(
        f'An immediate-or-cancel {order_type} order cannot carry an order_expiry: '
        'it never rests, so the venue requires none. Drop `order_expiry`, or use '
        "'good-till-time' / 'post-only'."
      )
    expiry = 0
  elif order_expiry is not None:
    expiry = epoch_millis(order_expiry, 'order_expiry')
  else:
    expiry = default_expiry
  return OrderInfo(
    market_index=market_index,
    client_order_index=client_order_index,
    base_amount=base_amount,
    price=price,
    is_ask=int(is_ask),
    type=choose(ORDER_TYPES, order_type, 'order_type'),
    time_in_force=choose(TIME_IN_FORCE, tif, 'time_in_force'),
    reduce_only=int(reduce_only),
    trigger_price=trigger_price,
    order_expiry=expiry,
  )


def primary_info(
  primary: 'GroupPrimaryOrder', *, order_expiry: datetime | None, default_expiry: int
) -> OrderInfo:
  """A group's primary order; only a resting limit order carries the group's expiry."""
  time_in_force = primary['time_in_force'] if primary['order_type'] == 'limit' else None
  resting = primary['order_type'] == 'limit' and time_in_force != 'immediate-or-cancel'
  return order_info(
    market_index=primary['market_index'],
    client_order_index=primary.get('client_order_index', 0),
    base_amount=primary['base_amount'],
    price=primary['price'],
    is_ask=primary['is_ask'],
    order_type=primary['order_type'],
    time_in_force=time_in_force,
    reduce_only=primary.get('reduce_only', False),
    trigger_price=0,
    order_expiry=order_expiry if resting else None,
    default_expiry=default_expiry,
  )


def leg_info(
  leg: 'GroupLeg',
  *,
  market_index: int,
  base_amount: int,
  is_ask: bool,
  order_expiry: datetime | None,
  default_expiry: int,
) -> OrderInfo:
  """A group's stop-loss or take-profit order.

  Every child is reduce-only: OTO and OTOCO children carry no size of their own (they
  inherit the primary's fill), which the venue accepts only on a reduce-only order, and
  OCO legs close a position by definition.
  """
  return order_info(
    market_index=market_index,
    client_order_index=leg.get('client_order_index', 0),
    base_amount=base_amount,
    price=leg['price'],
    is_ask=is_ask,
    order_type=leg['order_type'],
    time_in_force=None,
    reduce_only=True,
    trigger_price=leg['trigger_price'],
    order_expiry=order_expiry,
    default_expiry=default_expiry,
  )


def group_infos(group: 'OrderGroup', *, default_expiry: int) -> tuple[OrderInfo, ...]:
  """The orders of a `client.tx.create_grouped_orders` group, primary first.

  OTO and OTOCO children take the primary's market and the opposite side, with no size of
  their own (they inherit the primary's fill); every child is reduce-only (`leg_info`).
  """
  expiry = group.get('order_expiry')
  if group['grouping_type'] == 'oco':
    legs = (group['stop_loss'], group['take_profit'])
    return tuple(
      leg_info(
        leg,
        market_index=group['market_index'],
        base_amount=group['base_amount'],
        is_ask=group['is_ask'],
        order_expiry=expiry,
        default_expiry=default_expiry,
      )
      for leg in legs
    )
  primary = group['primary']
  if group['grouping_type'] == 'oto':
    children: tuple['GroupLeg', ...] = (group['trigger'],)
  else:
    children = (group['stop_loss'], group['take_profit'])
  first = primary_info(primary, order_expiry=expiry, default_expiry=default_expiry)
  return (
    first,
    *(
      leg_info(
        leg,
        market_index=primary['market_index'],
        base_amount=0,
        is_ask=not primary['is_ask'],
        order_expiry=expiry,
        default_expiry=default_expiry,
      )
      for leg in children
    ),
  )


@dataclass(frozen=True, kw_only=True)
class AccountSigner:
  """Signs for one Lighter account on one network, with one or more API keys.

  Examples:
    ```python
    async with Lighter.new(network='testnet') as client:
      next_nonce = await client.api.account.keys.next_nonce(
        account_index=client.signer.account_index, api_key_index=4
      )
      signed = client.signer.cancel_order(  # market 4095: testnet's ETH perp
        market_index=4095, order_index=123, nonce=next_nonce['nonce'], api_key_index=4
      )  # submit before it expires (10 minutes by default, `expires_at`)
      token = client.signer.auth_token()
    ```
  """

  account_index: int
  """Account every signature is made for."""
  chain_id: int
  """Chain id of the network, mixed into every transaction hash."""
  keys: Mapping[int, Signer] = field(repr=False)
  """API keys by slot, in rotation order; the first also signs auth tokens."""
  eth_private_key: str | None = field(default=None, repr=False)
  """L1 wallet key, for the transactions that carry an Ethereum signature too."""

  @classmethod
  def new(
    cls,
    *,
    account_index: int,
    api_keys: Mapping[int, str | Signer],
    chain_id: int,
    eth_private_key: str | None = None,
  ) -> 'AccountSigner':
    """Bind API keys to one account and network.

    Args:
      account_index: Account the keys belong to.
      api_keys: API keys by slot: a hex private key (signed with `PythonSigner`), or any
        other `Signer`.
      chain_id: Chain id of the network the keys sign for.
      eth_private_key: L1 wallet key, needed only by the L1-signed transactions.

    Raises:
      AuthError: No API key was given, or a private key is malformed.
    """
    if not api_keys:
      raise AuthError('No API keys: pass at least one `api_keys={index: private_key}`.')
    keys: dict[int, Signer] = {}
    for index, key in api_keys.items():
      if isinstance(key, str):
        try:
          keys[index] = PythonSigner.from_hex(key)
        except AuthError as e:
          raise AuthError(f'API key {index}: {e.args[0]}') from None
      else:
        keys[index] = key
    return cls(
      account_index=account_index,
      chain_id=chain_id,
      keys=keys,
      eth_private_key=eth_private_key,
    )

  @property
  def api_key_indices(self) -> tuple[int, ...]:
    """Configured API key slots, in rotation order."""
    return tuple(self.keys)

  def key(self, api_key_index: int | None) -> int:
    """The slot to sign with: `api_key_index` if given, else the first configured one.

    Args:
      api_key_index: Requested slot, or `None` for the default.
    """
    return self.api_key_indices[0] if api_key_index is None else api_key_index

  def key_signer(self, api_key_index: int) -> Signer:
    """The key in a slot.

    Args:
      api_key_index: Slot to look up.

    Raises:
      AuthError: No key is configured for that slot.
    """
    signer = self.keys.get(api_key_index)
    if signer is None:
      raise AuthError(
        f'API key {api_key_index} of account {self.account_index} is not configured'
      )
    return signer

  def sign(
    self, tx: L2Tx, *, verify: bool = False, key: Signer | None = None
  ) -> SignedTx:
    """Sign any transaction object with the key of its `api_key_index`.

    The L1 signature of a transaction that can carry one is added when `eth_private_key`
    is configured (after the transaction validates, so the wallet never signs an invalid
    one); otherwise its `L1Sig` stays empty and `message_to_sign` is left for the caller.

    Args:
      tx: The transaction, built with this account's index.
      verify: Check the new L2 signature against the key's public key before returning.
      key: Sign with this key instead of the configured key of `tx.api_key_index` (a
        `ChangePubKey` is signed by the key it registers).

    Raises:
      AuthError: No key is configured for the transaction's slot.
      BadRequest: The transaction breaks one of lighter-go's validation rules.
    """
    signer = key if key is not None else self.key_signer(tx.api_key_index)
    l1_signature = ''
    message = tx.l1_message(self.chain_id)
    if message is not None and self.eth_private_key is not None:
      tx.validate()
      l1_signature = eth_sign(message, eth_private_key=self.eth_private_key)
    return tx.sign(
      signer,
      chain_id=self.chain_id,
      l1_signature=l1_signature,
      verify_with=signer.public_key if verify else None,
    )

  def base(
    self,
    *,
    nonce: int,
    api_key_index: int | None,
    expires_at: datetime | None,
  ) -> BaseFields:
    """The fields every transaction carries (`account_index`, key, nonce, `expired_at`)."""
    expiry = expires_at or datetime.now(timezone.utc) + DEFAULT_TX_LIFETIME
    return BaseFields(
      account_index=self.account_index,
      api_key_index=self.key(api_key_index),
      nonce=nonce,
      expired_at=epoch_millis(expiry, 'expires_at'),
    )

  def generate_api_key(self) -> ApiKeyPair:
    """Generate a fresh API key pair locally; register it with `change_api_key`."""
    return generate_api_key()

  def auth_token(
    self,
    *,
    expires_at: datetime | None = None,
    lifetime: timedelta = timedelta(minutes=10),
    api_key_index: int | None = None,
  ) -> str:
    """Build a standard auth token, for private REST reads, token-gated writes and private streams.

    A token carries only its expiry and is valid from the moment it is signed until then.
    Lighter checks, on every request, that the expiry is at most 8 hours ahead, so a token
    cannot be signed now for a later window.

    Args:
      expires_at: Absolute expiry, at most 8 hours from now.
      lifetime: Expiry relative to now, when `expires_at` is not given.
      api_key_index: Slot to sign with; defaults to the first configured one.

    Raises:
      BadRequest: The expiry is more than 8 hours from now (Lighter would reject the token
        with `20013 invalid auth: invalid deadline`), or `expires_at` is a naive datetime.
      AuthError: No key is configured for `api_key_index`.
    """
    deadline = (
      aware(expires_at, 'expires_at')
      if expires_at is not None
      else datetime.now(timezone.utc) + lifetime
    )
    if deadline - datetime.now(timezone.utc) > MAX_AUTH_TOKEN_LIFETIME:
      raise BadRequest('Lighter auth tokens expire at most 8 hours from now')
    index = self.key(api_key_index)
    return auth_token(
      self.key_signer(index),
      deadline=deadline,
      account_index=self.account_index,
      api_key_index=index,
    )

  # ---------------------------------------------------------------- orders

  def create_order(
    self,
    order: 'NewOrder',
    *,
    integrator: Integrator | None = None,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign an order (`L2CreateOrder`, tx type 14): `client.tx.create_order`'s twin.

    Args:
      order: The order, exactly as `client.tx.create_order` takes it (`LimitOrder`,
        `IocLimitOrder`, `MarketOrder`, `StopLossOrder`, ... from
        `typed_lighter.tx.create_order`): prices and sizes are integers scaled by the
        market's decimals (`client.scaler`).
      integrator: Integrator fees to charge on this order.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, a
        closed-set argument is outside its set, the order misses a required key, or an
        untyped immediate-or-cancel order carries an `order_expiry` (`IocLimitOrder` and
        `MarketOrder` have no such field).

    Examples:
      ```python
      signed = client.signer.create_order(
        {
          'order_type': 'limit',
          'market_index': 0,
          'client_order_index': 1,
          'base_amount': 1_000,
          'is_ask': False,
          'price': 250_000,
          'time_in_force': 'post-only',
        },
        nonce=nonce,  # the key's next nonce (`api.account.keys.next_nonce`)
      )
      ```

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/trading)
    """
    with reading('order'):
      default_expiry = epoch_millis(datetime.now(timezone.utc) + DEFAULT_ORDER_LIFETIME)
      return self.sign(
        CreateOrder(
          **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
          attributes=self.order_attributes(
            skip_nonce=skip_nonce,
            self_trade_behavior=order.get('self_trade_behavior', 'expire-maker'),
            self_trade_equality=order.get('self_trade_equality', 'account'),
            integrator=integrator,
          ),
          order=order_info(
            market_index=order['market_index'],
            client_order_index=order['client_order_index'],
            base_amount=order['base_amount'],
            price=order['price'],
            is_ask=order['is_ask'],
            order_type=order['order_type'],
            time_in_force=order['time_in_force'] if 'time_in_force' in order else None,
            reduce_only=order.get('reduce_only', False),
            trigger_price=order['trigger_price'] if 'trigger_price' in order else 0,
            order_expiry=order.get('order_expiry'),
            default_expiry=default_expiry,
          ),
        )
      )

  def create_grouped_orders(
    self,
    group: 'OrderGroup',
    *,
    self_trade_behavior: SelfTradeBehavior = 'expire-maker',
    self_trade_equality: SelfTradeEquality = 'account',
    integrator: Integrator | None = None,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign an order group (`L2CreateGroupedOrders`, tx type 28): `client.tx.create_grouped_orders`' twin.

    - `oto`: a limit/market primary, then one opposite-side stop-loss or take-profit,
      placed once the primary fills and sized by the fill.
    - `oco`: a reduce-only stop-loss and take-profit of one size and side; one filling
      cancels the other.
    - `otoco`: a primary, then an opposite-side stop-loss and take-profit pair, sized by
      the fill, that cancel each other.

    Args:
      group: The group, exactly as `client.tx.create_grouped_orders` takes it (`OtoGroup`,
        `OcoGroup` or `OtocoGroup` from `typed_lighter.tx.create_grouped_orders`).
      self_trade_behavior: What happens on a self-match.
      self_trade_equality: What counts as a self-match.
      integrator: Integrator fees to charge on the group.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, a
        closed-set argument is outside its set, or the argument misses a required key.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/trading)
    """
    default_expiry = epoch_millis(datetime.now(timezone.utc) + DEFAULT_ORDER_LIFETIME)
    with reading('group'):
      return self.sign(
        CreateGroupedOrders(
          **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
          attributes=self.order_attributes(
            skip_nonce=skip_nonce,
            self_trade_behavior=self_trade_behavior,
            self_trade_equality=self_trade_equality,
            integrator=integrator,
          ),
          grouping_type=choose(GROUPING_TYPES, group['grouping_type'], 'grouping_type'),
          orders=group_infos(group, default_expiry=default_expiry),
        )
      )

  def cancel_order(
    self,
    *,
    market_index: int,
    order_index: int,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign an order cancellation (`L2CancelOrder`, tx type 15).

    Args:
      market_index: Market id of the order.
      order_index: The order's `order_index` (or its `client_order_index`).
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/trading)
    """
    return self.sign(
      CancelOrder(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        market_index=market_index,
        index=order_index,
      )
    )

  def cancel_all_orders(
    self,
    cancel: 'CancelAll',
    *,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign a cancel-all (`L2CancelAllOrders`, tx type 16): `client.tx.cancel_all_orders`' twin.

    Args:
      cancel: Cancel now (`{'mode': 'immediate'}`, optionally one `market_index`), schedule
        a cancel-all at `cancel_at` (a dead man's switch, pushed back by signing a new one),
        or abort the scheduled one, exactly as `client.tx.cancel_all_orders` takes it.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, a
        closed-set argument is outside its set, or the argument misses a required key.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/trading)
    """
    with reading('cancel'):
      mode: CancelAllMode = cancel['mode']
      cancel_at = cancel['cancel_at'] if cancel['mode'] == 'scheduled' else None
      market_index = (
        cancel.get('market_index') if cancel['mode'] == 'immediate' else None
      )
      return self.sign(
        CancelAllOrders(
          **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
          attributes=Attributes(
            skip_nonce=1 if skip_nonce else None,
            cancel_all_market_index=market_index,
          ),
          time_in_force=choose(CANCEL_ALL_MODES, mode, 'mode'),
          time=0 if cancel_at is None else epoch_millis(cancel_at, 'cancel_at'),
        )
      )

  def modify_order(
    self,
    *,
    market_index: int,
    order_index: int,
    base_amount: int,
    price: int,
    trigger_price: int = 0,
    order_version: int | None = None,
    self_trade_behavior: SelfTradeBehavior = 'expire-maker',
    self_trade_equality: SelfTradeEquality = 'account',
    integrator: Integrator | None = None,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign an order modification (`L2ModifyOrder`, tx type 17).

    Args:
      market_index: Market id of the order.
      order_index: The order's `order_index` (or its `client_order_index`).
      base_amount: New scaled size.
      price: New scaled price.
      trigger_price: New scaled trigger price, for stop-loss/take-profit orders.
      order_version: Only modify the order if it is still at this version.
      self_trade_behavior: What happens on a self-match.
      self_trade_equality: What counts as a self-match.
      integrator: Integrator fees to charge.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/trading)
    """
    attributes = self.order_attributes(
      skip_nonce=skip_nonce,
      self_trade_behavior=self_trade_behavior,
      self_trade_equality=self_trade_equality,
      integrator=integrator,
      order_version=order_version,
    )
    return self.sign(
      ModifyOrder(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=attributes,
        market_index=market_index,
        index=order_index,
        base_amount=base_amount,
        price=price,
        trigger_price=trigger_price,
      )
    )

  def order_attributes(
    self,
    *,
    skip_nonce: bool,
    self_trade_behavior: SelfTradeBehavior,
    self_trade_equality: SelfTradeEquality,
    integrator: Integrator | None,
    order_version: int | None = None,
  ) -> Attributes:
    """Order attributes, set only when they differ from their nil value (as the shared library does)."""
    behavior = choose(SELF_TRADE_BEHAVIOR, self_trade_behavior, 'self_trade_behavior')
    equality = choose(SELF_TRADE_EQUALITY, self_trade_equality, 'self_trade_equality')
    return Attributes(
      integrator_account_index=(integrator['account_index'] or None)
      if integrator
      else None,
      integrator_taker_fee=(integrator['taker_fee'] or None) if integrator else None,
      integrator_maker_fee=(integrator['maker_fee'] or None) if integrator else None,
      skip_nonce=1 if skip_nonce else None,
      self_trade_behavior_mode=behavior or None,
      self_trade_equality_mode=equality or None,
      order_version=order_version or None,
    )

  # ---------------------------------------------------------------- positions

  def update_leverage(
    self,
    *,
    market_index: int,
    initial_margin_fraction: int,
    margin_mode: MarginMode,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign a leverage change (`L2UpdateLeverage`, tx type 20).

    Args:
      market_index: Market id.
      initial_margin_fraction: Initial margin fraction in 1e-4 units: 10_000 / leverage
        (e.g. 1_000 for 10x), in [1, 10_000].
      margin_mode: Cross or isolated margin for the market.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/trading)
    """
    return self.sign(
      UpdateLeverage(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        market_index=market_index,
        initial_margin_fraction=initial_margin_fraction,
        margin_mode=choose(MARGIN_MODES, margin_mode, 'margin_mode'),
      )
    )

  def update_margin(
    self,
    *,
    market_index: int,
    usdc_amount: int,
    direction: MarginDirection,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign an isolated-margin transfer (`L2UpdateMargin`, tx type 29).

    Args:
      market_index: Market id of the isolated position.
      usdc_amount: USDC amount in 1e-6 units.
      direction: Add to or remove from the position's margin.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/trading)
    """
    return self.sign(
      UpdateMargin(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        market_index=market_index,
        usdc_amount=usdc_amount,
        direction=1 if direction == 'add' else 0,
      )
    )

  # ---------------------------------------------------------------- account

  def change_api_key(
    self,
    api_private_key: str | Signer,
    *,
    api_key_index: int,
    nonce: int,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign an API key registration (`L2ChangePubKey`, tx type 8): `client.tx.change_api_key`'s twin.

    As in lighter-go, the new key signs the transaction (and the signature is checked
    against it), `api_key_index` is the slot being registered, and the nonce is that
    slot's own; the L1 wallet authorizes it. The slot needs no configured key, and only
    the new key's public half goes into the transaction.

    Args:
      api_private_key: The new key: a hex private key (e.g. from `generate_api_key`), or any
        `Signer`.
      api_key_index: Slot being (re-)registered.
      nonce: Nonce of that slot (`0` for a slot never used before).
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No `eth_private_key` is configured, or `api_private_key` is malformed.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/api-keys)
    """
    if self.eth_private_key is None:
      raise AuthError('change_api_key needs the L1 wallet key: pass `eth_private_key`.')
    key = (
      PythonSigner.from_hex(api_private_key)
      if isinstance(api_private_key, str)
      else api_private_key
    )
    return self.sign(
      ChangePubKey(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        pub_key=key.public_key,
      ),
      verify=True,
      key=key,
    )

  def create_sub_account(
    self,
    *,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign a sub-account creation (`L2CreateSubAccount`, tx type 9), from a master account.

    Args:
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/create-accounts-programmatically)
    """
    return self.sign(
      CreateSubAccount(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
      )
    )

  def update_account_config(
    self,
    account_trading_mode: AccountTradingMode,
    *,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign an account trading-mode change (`L2UpdateAccountConfig`, tx type 41).

    Args:
      account_trading_mode: Classic margin, or the unified trading account.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/account-types)
    """
    return self.sign(
      UpdateAccountConfig(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        account_trading_mode=choose(
          ACCOUNT_TRADING_MODES, account_trading_mode, 'account_trading_mode'
        ),
      )
    )

  def update_account_asset_config(
    self,
    *,
    asset_index: int,
    use_as_margin: bool,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign an asset-as-margin switch (`L2UpdateAccountAssetConfig`, tx type 42).

    Args:
      asset_index: Asset id.
      use_as_margin: Count the asset as margin, or not.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/trading)
    """
    return self.sign(
      UpdateAccountAssetConfig(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        asset_index=asset_index,
        asset_margin_mode=int(use_as_margin),
      )
    )

  def approve_integrator(
    self,
    *,
    integrator_account_index: int,
    approval: 'IntegratorApprovalChange',
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign an integrator fee approval (`L2ApproveIntegrator`, tx type 45): `client.tx.approve_integrator`'s twin.

    L1-signed when `eth_private_key` is configured; the venue needs the L1 signature unless
    the integrator shares this account's master account or every fee is zero.

    Args:
      integrator_account_index: Integrator account.
      approval: Fee caps until an expiry, or `{'action': 'revoke'}` (the venue's all-zero
        caps with no expiry), exactly as `client.tx.approve_integrator` takes it.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, a
        closed-set argument is outside its set, or the argument misses a required key.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/partner-integration)
    """
    with reading('approval'):
      if approval['action'] == 'revoke':
        fees = (0, 0, 0, 0)
        expiry = 0
      else:
        fees = (
          approval['max_perps_taker_fee'],
          approval['max_perps_maker_fee'],
          approval['max_spot_taker_fee'],
          approval['max_spot_maker_fee'],
        )
        expiry = epoch_millis(approval['approval_expiry'], 'approval_expiry')
      return self.sign(
        ApproveIntegrator(
          **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
          attributes=Attributes(skip_nonce=1 if skip_nonce else None),
          integrator_account_index=integrator_account_index,
          max_perps_taker_fee=fees[0],
          max_perps_maker_fee=fees[1],
          max_spot_taker_fee=fees[2],
          max_spot_maker_fee=fees[3],
          approval_expiry=expiry,
        ),
        verify=True,
      )

  # ---------------------------------------------------------------- assets

  def transfer(
    self,
    *,
    to_account_index: int,
    amount: int,
    asset_index: int = 3,
    from_route: Route = 'perps',
    to_route: Route = 'perps',
    usdc_fee: int = 0,
    memo: str = '00' * 32,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign a transfer (`L2Transfer`, tx type 12).

    L1-signed when `eth_private_key` is configured; the venue needs the L1 signature unless
    both accounts share the same master account.

    Args:
      to_account_index: Receiving account.
      amount: Amount in the asset's smallest unit (1e-6 for USDC).
      asset_index: Asset id (3 is USDC).
      from_route: Perps or spot side of this account.
      to_route: Perps or spot side of the receiving account.
      usdc_fee: Transfer fee in 1e-6 USDC (`GET /api/v1/transferFeeInfo`).
      memo: Exactly 32 bytes as hex (`0x` optional), shown in the L1 message but not part of
        the L2 hash.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/deposits-transfers-and-withdrawals)
    """
    return self.sign(
      Transfer(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        to_account_index=to_account_index,
        asset_index=asset_index,
        from_route_type=choose(ROUTES, from_route, 'from_route'),
        to_route_type=choose(ROUTES, to_route, 'to_route'),
        amount=amount,
        usdc_fee=usdc_fee,
        memo=hex_bytes(memo),
      )
    )

  def withdraw(
    self,
    *,
    amount: int,
    asset_index: int = 3,
    route: Route = 'perps',
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign a secure withdrawal to the account's own L1 address (`L2Withdraw`, tx type 13).

    Args:
      amount: Amount in the asset's smallest unit (1e-6 for USDC).
      asset_index: Asset id (3 is USDC).
      route: Perps or spot side of the account.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/deposits-transfers-and-withdrawals)
    """
    return self.sign(
      Withdraw(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        asset_index=asset_index,
        route_type=choose(ROUTES, route, 'route'),
        amount=amount,
      )
    )

  def stake(
    self,
    *,
    staking_pool_index: int,
    share_amount: int,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign a stake into a staking pool (`L2StakeAssets`, tx type 35).

    Args:
      staking_pool_index: Staking pool account.
      share_amount: Shares to stake.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/manage-public-pools-shares)
    """
    return self.sign(
      StakeAssets(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        staking_pool_index=staking_pool_index,
        share_amount=share_amount,
      )
    )

  def unstake(
    self,
    *,
    staking_pool_index: int,
    share_amount: int,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign an unstake from a staking pool (`L2UnstakeAssets`, tx type 36).

    Args:
      staking_pool_index: Staking pool account.
      share_amount: Shares to redeem.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/manage-public-pools-shares)
    """
    return self.sign(
      UnstakeAssets(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        staking_pool_index=staking_pool_index,
        share_amount=share_amount,
      )
    )

  # ---------------------------------------------------------------- public pools

  def create_public_pool(
    self,
    *,
    operator_fee: int,
    initial_total_shares: int,
    min_operator_share_rate: int,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign a public pool creation (`L2CreatePublicPool`, tx type 10), from a master account.

    Args:
      operator_fee: Operator fee in 1e-6 units.
      initial_total_shares: Initial share supply (one share is 0.001 USDC).
      min_operator_share_rate: Minimum operator share in 1e-4 units (at most 10_000).
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/manage-public-pools-shares)
    """
    return self.sign(
      CreatePublicPool(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        operator_fee=operator_fee,
        initial_total_shares=initial_total_shares,
        min_operator_share_rate=min_operator_share_rate,
      )
    )

  def update_public_pool(
    self,
    *,
    public_pool_index: int,
    status: PoolStatus,
    operator_fee: int,
    min_operator_share_rate: int,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign a public pool update (`L2UpdatePublicPool`, tx type 11).

    Args:
      public_pool_index: Pool account.
      status: Active or frozen.
      operator_fee: Operator fee in 1e-6 units.
      min_operator_share_rate: Minimum operator share in 1e-4 units (at most 10_000).
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/manage-public-pools-shares)
    """
    return self.sign(
      UpdatePublicPool(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        public_pool_index=public_pool_index,
        status=choose(POOL_STATUSES, status, 'status'),
        operator_fee=operator_fee,
        min_operator_share_rate=min_operator_share_rate,
      )
    )

  def mint_shares(
    self,
    *,
    public_pool_index: int,
    share_amount: int,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign a public pool share purchase (`L2MintShares`, tx type 18).

    Args:
      public_pool_index: Pool account.
      share_amount: Shares to mint.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/manage-public-pools-shares)
    """
    return self.sign(
      MintShares(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        public_pool_index=public_pool_index,
        share_amount=share_amount,
      )
    )

  def burn_shares(
    self,
    *,
    public_pool_index: int,
    share_amount: int,
    nonce: int,
    api_key_index: int | None = None,
    skip_nonce: bool = False,
    expires_at: datetime | None = None,
  ) -> SignedTx:
    """Sign a public pool share redemption (`L2BurnShares`, tx type 19).

    Args:
      public_pool_index: Pool account.
      share_amount: Shares to burn.
      nonce: Nonce of `api_key_index`.
      api_key_index: Slot to sign with.
      skip_nonce: Accept any increasing nonce.
      expires_at: When the sequencer stops accepting the transaction.

    Raises:
      AuthError: No key is configured for `api_key_index`.
      BadRequest: The transaction breaks one of lighter-go's validation rules, or a
        closed-set argument is outside its set.

    References:
      - [Official docs](https://apidocs.lighter.xyz/docs/manage-public-pools-shares)
    """
    return self.sign(
      BurnShares(
        **self.base(nonce=nonce, api_key_index=api_key_index, expires_at=expires_at),
        attributes=Attributes(skip_nonce=1 if skip_nonce else None),
        public_pool_index=public_pool_index,
        share_amount=share_amount,
      )
    )
