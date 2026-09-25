"""Order transactions: create (14), cancel (15), cancel all (16), modify (17) and grouped (28).

Ported from lighter-go v1.0.10 `types/txtypes/{create_order,cancel_order,cancel_all_orders,
modify_order,create_grouped_orders}.go`, validation order and messages included.
"""

from typing_extensions import Any, ClassVar
from dataclasses import dataclass

from .. import field
from ..poseidon2 import HashOut, hash_no_pad, hash_two_to_one
from .base import (
  ERR_ACCOUNT_INDEX_TOO_HIGH,
  ERR_ACCOUNT_INDEX_TOO_LOW,
  ERR_INVALID_MARKET_INDEX,
  ERR_PRICE_TOO_HIGH,
  ERR_PRICE_TOO_LOW,
  ERR_TRIGGER_PRICE_INVALID,
  MAX_CLIENT_ORDER_INDEX,
  MAX_GROUPED_ORDER_COUNT,
  MAX_ORDER_BASE_AMOUNT,
  MAX_ORDER_EXPIRY,
  MAX_ORDER_INDEX,
  MAX_ORDER_PRICE,
  MIN_ORDER_INDEX,
  GoType,
  L2Tx,
  check_account,
  check_api_key,
  check_go_int,
  check_int,
  check_market,
  check_nonce_and_expiry,
  fail,
)

LIMIT, MARKET, STOP_LOSS, STOP_LOSS_LIMIT, TAKE_PROFIT, TAKE_PROFIT_LIMIT, TWAP = range(
  7
)
"""Order types (`LimitOrder` .. `TWAPOrder`)."""
IMMEDIATE_OR_CANCEL, GOOD_TILL_TIME, POST_ONLY = range(3)
"""Order times in force."""
IMMEDIATE_CANCEL_ALL, SCHEDULED_CANCEL_ALL, ABORT_SCHEDULED_CANCEL_ALL = range(3)
"""Cancel-all times in force."""
ONE_TRIGGERS_THE_OTHER, ONE_CANCELS_THE_OTHER, ONE_TRIGGERS_A_ONE_CANCELS_THE_OTHER = (
  1,
  2,
  3,
)
"""Grouping types (OTO, OCO, OTOCO)."""

ERR_BASE_AMOUNT_TOO_LOW = 'BaseAmount should not be less than 1'
ERR_BASE_AMOUNT_TOO_HIGH = (
  f'BaseAmount should not be larger than {MAX_ORDER_BASE_AMOUNT}'
)
ERR_CLIENT_ORDER_INDEX_TOO_LOW = 'ClientOrderIndex should not be less than 1'
ERR_CLIENT_ORDER_INDEX_TOO_HIGH = (
  f'ClientOrderIndex should not be larger than {MAX_CLIENT_ORDER_INDEX}'
)
ERR_IS_ASK_INVALID = 'IsAsk should be 0 or 1'
ERR_TIME_IN_FORCE_INVALID = 'OrderTimeInForce is not valid'
ERR_REDUCE_ONLY_INVALID = 'ReduceOnly is invalid'
ERR_ORDER_EXPIRY_INVALID = 'OrderExpiry is invalid'
ERR_ORDER_TYPE_INVALID = 'OrderType is not valid'
ERR_GROUP_SIZE_INVALID = 'OrderGroupSize is not valid'


@dataclass(frozen=True, kw_only=True)
class OrderInfo:
  """One order's fields (Go `OrderInfo`): the body of a create order, and each grouped order."""

  market_index: int
  """Market id."""
  client_order_index: int
  """Caller-chosen order id in [1, 2^48 - 1], or 0 for none."""
  base_amount: int
  """Size, scaled by the market's size decimals (0 only for a reduce-only order)."""
  price: int
  """Price, scaled by the market's price decimals (`uint32`)."""
  is_ask: int
  """1 sell, 0 buy."""
  type: int
  """Order type (`LIMIT` .. `TWAP`)."""
  time_in_force: int
  """Time in force (`IMMEDIATE_OR_CANCEL`, `GOOD_TILL_TIME`, `POST_ONLY`)."""
  reduce_only: int
  """1: only ever reduce the position."""
  trigger_price: int
  """Scaled trigger price for stop-loss/take-profit orders, else 0 (`uint32`)."""
  order_expiry: int
  """Epoch milliseconds, or 0 for none."""

  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('market_index', 'MarketIndex', 'int16'),
    ('client_order_index', 'ClientOrderIndex', 'int64'),
    ('base_amount', 'BaseAmount', 'int64'),
    ('is_ask', 'IsAsk', 'uint8'),
    ('type', 'Type', 'uint8'),
    ('time_in_force', 'TimeInForce', 'uint8'),
    ('reduce_only', 'ReduceOnly', 'uint8'),
    ('order_expiry', 'OrderExpiry', 'int64'),
  )

  def check_types(self):
    """Reject values the Go `OrderInfo` fields could not hold (prices: see `check_int`)."""
    for name, go_name, go_type in self.GO_FIELDS:
      check_go_int(go_name, getattr(self, name), go_type)
    check_int('Price', self.price)
    check_int('TriggerPrice', self.trigger_price)

  def elements(self) -> list[int]:
    """The order's fields in hash (and declaration) order."""
    return [
      self.market_index,
      self.client_order_index,
      self.base_amount,
      self.price,
      self.is_ask,
      self.type,
      self.time_in_force,
      self.reduce_only,
      self.trigger_price,
      self.order_expiry,
    ]

  def to_json(self) -> dict[str, Any]:
    """Go's JSON for an `OrderInfo`."""
    return {
      'MarketIndex': self.market_index,
      'ClientOrderIndex': self.client_order_index,
      'BaseAmount': self.base_amount,
      'Price': self.price,
      'IsAsk': self.is_ask,
      'Type': self.type,
      'TimeInForce': self.time_in_force,
      'ReduceOnly': self.reduce_only,
      'TriggerPrice': self.trigger_price,
      'OrderExpiry': self.order_expiry,
    }

  def hash(self) -> HashOut:
    """Go `HashNoPad` of the order's fields, as `CreateGroupedOrders` folds them."""
    return hash_no_pad([field.from_go_int(x) for x in self.elements()])


def check_client_order_index(value: int):
  """0 (none), or [1, 2^48 - 1]."""
  if value != 0:
    if value < 1:
      fail(ERR_CLIENT_ORDER_INDEX_TOO_LOW)
    if value > MAX_CLIENT_ORDER_INDEX:
      fail(ERR_CLIENT_ORDER_INDEX_TOO_HIGH)


def check_base_amount(order: OrderInfo):
  """Size in [1, 2^48 - 1]; 0 only for a reduce-only order."""
  if order.reduce_only != 1 and order.base_amount == 0:
    fail(ERR_BASE_AMOUNT_TOO_LOW)
  if order.base_amount != 0 and order.base_amount < 1:
    fail(ERR_BASE_AMOUNT_TOO_LOW)
  if order.base_amount > MAX_ORDER_BASE_AMOUNT:
    fail(ERR_BASE_AMOUNT_TOO_HIGH)


def check_price(price: int):
  """Price in [1, 2^32 - 1]."""
  if price < 1:
    fail(ERR_PRICE_TOO_LOW)
  if price > MAX_ORDER_PRICE:
    fail(ERR_PRICE_TOO_HIGH)


def check_trigger_price_range(trigger_price: int):
  """0 (none), or [1, 2^32 - 1]."""
  if (trigger_price < 1 or trigger_price > MAX_ORDER_PRICE) and trigger_price != 0:
    fail(ERR_TRIGGER_PRICE_INVALID)


def check_order_expiry_range(order_expiry: int):
  """0 (none), or [1, 2^63 - 1]."""
  if (order_expiry < 1 or order_expiry > MAX_ORDER_EXPIRY) and order_expiry != 0:
    fail(ERR_ORDER_EXPIRY_INVALID)


def check_order_fields(order: OrderInfo):
  """The range checks `CreateOrder` and every grouped order share, in Go's order."""
  check_client_order_index(order.client_order_index)
  check_base_amount(order)
  check_price(order.price)
  if order.is_ask not in (0, 1):
    fail(ERR_IS_ASK_INVALID)
  if order.time_in_force not in (IMMEDIATE_OR_CANCEL, GOOD_TILL_TIME, POST_ONLY):
    fail(ERR_TIME_IN_FORCE_INVALID)
  if order.reduce_only not in (0, 1):
    fail(ERR_REDUCE_ONLY_INVALID)
  check_order_expiry_range(order.order_expiry)


def check_parent_order(order: OrderInfo):
  """Go `ValidateParentOrder` (a grouped order's primary): market or limit only."""
  if order.type == MARKET:
    if order.time_in_force != IMMEDIATE_OR_CANCEL:
      fail(ERR_TIME_IN_FORCE_INVALID)
    elif order.order_expiry != 0:
      fail(ERR_ORDER_EXPIRY_INVALID)
    elif order.trigger_price != 0:
      fail(ERR_TRIGGER_PRICE_INVALID)
  elif order.type == LIMIT:
    if order.trigger_price != 0:
      fail(ERR_TRIGGER_PRICE_INVALID)
    elif order.time_in_force == IMMEDIATE_OR_CANCEL and order.order_expiry != 0:
      fail(ERR_ORDER_EXPIRY_INVALID)
    elif order.time_in_force != IMMEDIATE_OR_CANCEL and order.order_expiry == 0:
      fail(ERR_ORDER_EXPIRY_INVALID)
  else:
    fail(ERR_ORDER_TYPE_INVALID)


def check_child_order(order: OrderInfo):
  """Go `ValidateChildOrder`: a stop-loss or take-profit (plain or limit)."""
  if order.type in (STOP_LOSS, TAKE_PROFIT):
    if order.time_in_force != IMMEDIATE_OR_CANCEL:
      fail(ERR_TIME_IN_FORCE_INVALID)
    elif order.trigger_price == 0:
      fail(ERR_TRIGGER_PRICE_INVALID)
    elif order.order_expiry == 0:
      fail(ERR_ORDER_EXPIRY_INVALID)
  elif order.type in (STOP_LOSS_LIMIT, TAKE_PROFIT_LIMIT):
    if order.trigger_price == 0:
      fail(ERR_TRIGGER_PRICE_INVALID)
    elif order.order_expiry == 0:
      fail(ERR_ORDER_EXPIRY_INVALID)
  else:
    fail(ERR_ORDER_TYPE_INVALID)


def check_sibling_orders(orders: tuple[OrderInfo, ...]):
  """Go `ValidateSiblingOrders`: exactly one stop-loss and one take-profit."""
  if len(orders) != 2:
    fail(ERR_GROUP_SIZE_INVALID)
  has_stop_loss = has_take_profit = False
  for order in orders:
    check_child_order(order)
    if order.type in (STOP_LOSS, STOP_LOSS_LIMIT):
      has_stop_loss = True
    elif order.type in (TAKE_PROFIT, TAKE_PROFIT_LIMIT):
      has_take_profit = True
  if not has_stop_loss or not has_take_profit:
    fail(ERR_ORDER_TYPE_INVALID)


@dataclass(frozen=True, kw_only=True)
class CreateOrder(L2Tx):
  """`L2CreateOrder` (tx type 14)."""

  order: OrderInfo
  """The order."""

  TX_TYPE: ClassVar[int] = 14

  def check_types(self):
    """Go integer type checks, including the order's."""
    super().check_types()
    self.order.check_types()

  def check(self):
    """Go `L2CreateOrderTxInfo.Validate`."""
    o = self.order
    check_account(
      self.account_index, low=ERR_ACCOUNT_INDEX_TOO_LOW, high=ERR_ACCOUNT_INDEX_TOO_HIGH
    )
    check_api_key(self.api_key_index)
    check_market(o.market_index)
    check_order_fields(o)
    if o.type == MARKET:
      if o.time_in_force != IMMEDIATE_OR_CANCEL:
        fail(ERR_TIME_IN_FORCE_INVALID)
      elif o.order_expiry != 0:
        fail(ERR_ORDER_EXPIRY_INVALID)
      elif o.trigger_price != 0:
        fail(ERR_TRIGGER_PRICE_INVALID)
    elif o.type == LIMIT:
      if o.trigger_price != 0:
        fail(ERR_TRIGGER_PRICE_INVALID)
      elif o.time_in_force == IMMEDIATE_OR_CANCEL and o.order_expiry != 0:
        fail(ERR_ORDER_EXPIRY_INVALID)
      elif o.time_in_force != IMMEDIATE_OR_CANCEL and o.order_expiry == 0:
        fail(ERR_ORDER_EXPIRY_INVALID)
    elif o.type in (STOP_LOSS, TAKE_PROFIT):
      if o.time_in_force != IMMEDIATE_OR_CANCEL:
        fail(ERR_TIME_IN_FORCE_INVALID)
      elif o.trigger_price == 0:
        fail(ERR_TRIGGER_PRICE_INVALID)
      elif o.order_expiry == 0:
        fail(ERR_ORDER_EXPIRY_INVALID)
    elif o.type in (STOP_LOSS_LIMIT, TAKE_PROFIT_LIMIT):
      if o.trigger_price == 0:
        fail(ERR_TRIGGER_PRICE_INVALID)
      elif o.order_expiry == 0:
        fail(ERR_ORDER_EXPIRY_INVALID)
    elif o.type == TWAP:
      if o.time_in_force != GOOD_TILL_TIME:
        fail(ERR_TIME_IN_FORCE_INVALID)
      elif o.trigger_price != 0:
        fail(ERR_TRIGGER_PRICE_INVALID)
      elif o.order_expiry == 0:
        fail(ERR_ORDER_EXPIRY_INVALID)
    else:
      fail(ERR_ORDER_TYPE_INVALID)
    check_trigger_price_range(o.trigger_price)
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """The order's fields."""
    return self.order.elements()

  def body_json(self) -> dict[str, Any]:
    """The embedded `OrderInfo`, flattened."""
    return self.order.to_json()


@dataclass(frozen=True, kw_only=True)
class CancelOrder(L2Tx):
  """`L2CancelOrder` (tx type 15)."""

  market_index: int
  """Market id of the order."""
  index: int
  """The order's `order_index`, or its `client_order_index`."""

  TX_TYPE: ClassVar[int] = 15
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('market_index', 'MarketIndex', 'int16'),
    ('index', 'Index', 'int64'),
  )

  def check(self):
    """Go `L2CancelOrderTxInfo.Validate`."""
    check_account(
      self.account_index, low=ERR_ACCOUNT_INDEX_TOO_LOW, high=ERR_ACCOUNT_INDEX_TOO_HIGH
    )
    check_api_key(self.api_key_index)
    check_market(self.market_index)
    if self.index < 1 and self.index < MIN_ORDER_INDEX:
      fail(f'OrderIndex should not be less than {MIN_ORDER_INDEX}')
    if self.index > MAX_CLIENT_ORDER_INDEX and self.index > MAX_ORDER_INDEX:
      fail(f'OrderIndex should not be larger than {MAX_ORDER_INDEX}')
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Market, index."""
    return [self.market_index, self.index]

  def body_json(self) -> dict[str, Any]:
    """Market, index."""
    return {'MarketIndex': self.market_index, 'Index': self.index}


@dataclass(frozen=True, kw_only=True)
class CancelAllOrders(L2Tx):
  """`L2CancelAllOrders` (tx type 16): now, scheduled (dead man's switch), or abort a schedule."""

  time_in_force: int
  """`IMMEDIATE_CANCEL_ALL`, `SCHEDULED_CANCEL_ALL` or `ABORT_SCHEDULED_CANCEL_ALL`."""
  time: int
  """Epoch milliseconds of a scheduled cancel-all, else 0."""

  TX_TYPE: ClassVar[int] = 16
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('time_in_force', 'TimeInForce', 'uint8'),
    ('time', 'Time', 'int64'),
  )

  def check(self):
    """Go `L2CancelAllOrdersTxInfo.Validate`; the API key may be the nil key 255 here."""
    check_account(
      self.account_index, low=ERR_ACCOUNT_INDEX_TOO_LOW, high=ERR_ACCOUNT_INDEX_TOO_HIGH
    )
    check_api_key(self.api_key_index, allow_nil=True)
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)
    market = self.attributes.cancel_all_market_index
    if (
      market is not None
      and self.time_in_force != IMMEDIATE_CANCEL_ALL
      and market != 255
    ):
      fail(
        "Cancel all for market index can't be scheduled, TimeInforce must be ImmediateCancelAll"
      )
    if self.time_in_force == IMMEDIATE_CANCEL_ALL:
      if self.time != 0:
        fail('CancelAllTime should be nil')
    elif self.time_in_force == SCHEDULED_CANCEL_ALL:
      if self.time < 1 or self.time > MAX_ORDER_EXPIRY:
        fail(
          f'CancelAllTime should be larger than 0 and not larger than {MAX_ORDER_EXPIRY}'
        )
    elif self.time_in_force == ABORT_SCHEDULED_CANCEL_ALL:
      if self.time != 0:
        fail('CancelAllTime should be nil')
    else:
      fail('CancelAllTimeInForce is invalid')

  def body_elements(self) -> list[int]:
    """Time in force, time."""
    return [self.time_in_force, self.time]

  def body_json(self) -> dict[str, Any]:
    """Time in force, time."""
    return {'TimeInForce': self.time_in_force, 'Time': self.time}


@dataclass(frozen=True, kw_only=True)
class ModifyOrder(L2Tx):
  """`L2ModifyOrder` (tx type 17)."""

  market_index: int
  """Market id of the order."""
  index: int
  """The order's `order_index`, or its `client_order_index`."""
  base_amount: int
  """New size (scaled), or 0."""
  price: int
  """New price (scaled, `uint32`)."""
  trigger_price: int
  """New trigger price (scaled, `uint32`), or 0."""

  TX_TYPE: ClassVar[int] = 17
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('market_index', 'MarketIndex', 'int16'),
    ('index', 'Index', 'int64'),
    ('base_amount', 'BaseAmount', 'int64'),
  )

  def check_types(self):
    """Go integer type checks (prices: see `check_int`)."""
    super().check_types()
    check_int('Price', self.price)
    check_int('TriggerPrice', self.trigger_price)

  def check(self):
    """Go `L2ModifyOrderTxInfo.Validate`."""
    check_account(
      self.account_index, low=ERR_ACCOUNT_INDEX_TOO_LOW, high=ERR_ACCOUNT_INDEX_TOO_HIGH
    )
    check_api_key(self.api_key_index)
    check_market(self.market_index)
    if self.index < 1 and self.index < MIN_ORDER_INDEX:
      fail(ERR_CLIENT_ORDER_INDEX_TOO_LOW)
    if self.index > MAX_CLIENT_ORDER_INDEX and self.index > MAX_ORDER_INDEX:
      fail(ERR_CLIENT_ORDER_INDEX_TOO_HIGH)
    if self.base_amount != 0 and self.base_amount < 1:
      fail(ERR_BASE_AMOUNT_TOO_LOW)
    if self.base_amount > MAX_ORDER_BASE_AMOUNT:
      fail(ERR_BASE_AMOUNT_TOO_HIGH)
    check_price(self.price)
    check_trigger_price_range(self.trigger_price)
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)

  def body_elements(self) -> list[int]:
    """Market, index, size, price, trigger price."""
    return [
      self.market_index,
      self.index,
      self.base_amount,
      self.price,
      self.trigger_price,
    ]

  def body_json(self) -> dict[str, Any]:
    """Market, index, size, price, trigger price."""
    return {
      'MarketIndex': self.market_index,
      'Index': self.index,
      'BaseAmount': self.base_amount,
      'Price': self.price,
      'TriggerPrice': self.trigger_price,
    }


@dataclass(frozen=True, kw_only=True)
class CreateGroupedOrders(L2Tx):
  """`L2CreateGroupedOrders` (tx type 28): OTO, OCO or OTOCO order groups.

  The hash folds each order's own `HashNoPad` into one 4-element digest with `HashTwoToOne`
  (left to right), appended after the grouping type.
  """

  grouping_type: int
  """`ONE_TRIGGERS_THE_OTHER`, `ONE_CANCELS_THE_OTHER` or `ONE_TRIGGERS_A_ONE_CANCELS_THE_OTHER`."""
  orders: tuple[OrderInfo, ...]
  """The group's orders, primary first."""

  TX_TYPE: ClassVar[int] = 28
  GO_FIELDS: ClassVar[tuple[tuple[str, str, GoType], ...]] = (
    ('grouping_type', 'GroupingType', 'uint8'),
  )

  def check_types(self):
    """Go integer type checks, including every order's."""
    super().check_types()
    for order in self.orders:
      order.check_types()

  def check(self):
    """Go `L2CreateGroupedOrdersTxInfo.Validate`."""
    check_account(
      self.account_index, low=ERR_ACCOUNT_INDEX_TOO_LOW, high=ERR_ACCOUNT_INDEX_TOO_HIGH
    )
    check_api_key(self.api_key_index)
    orders = self.orders
    if len(orders) == 0 or len(orders) > MAX_GROUPED_ORDER_COUNT:
      fail(ERR_GROUP_SIZE_INVALID)
    check_market(orders[0].market_index)
    client_order_indices: set[int] = set()
    for order in orders:
      if order.market_index != orders[0].market_index:
        fail('MarketIndex should match the market index of the order')
      if order.client_order_index != 0:
        check_client_order_index(order.client_order_index)
        if order.client_order_index in client_order_indices:
          fail('ClientOrderIndex should be unique within the group')
        client_order_indices.add(order.client_order_index)
      check_base_amount(order)
      check_price(order.price)
      if order.is_ask not in (0, 1):
        fail(ERR_IS_ASK_INVALID)
      if order.time_in_force not in (IMMEDIATE_OR_CANCEL, GOOD_TILL_TIME, POST_ONLY):
        fail(ERR_TIME_IN_FORCE_INVALID)
      if order.reduce_only not in (0, 1):
        fail(ERR_REDUCE_ONLY_INVALID)
      check_order_expiry_range(order.order_expiry)
      check_trigger_price_range(order.trigger_price)
    check_nonce_and_expiry(nonce=self.nonce, expired_at=self.expired_at)
    if self.grouping_type == ONE_CANCELS_THE_OTHER:
      self.check_oco()
    elif self.grouping_type == ONE_TRIGGERS_THE_OTHER:
      self.check_oto()
    elif self.grouping_type == ONE_TRIGGERS_A_ONE_CANCELS_THE_OTHER:
      self.check_otoco()
    else:
      fail('GroupingType is not valid')

  def check_oco(self):
    """Go `ValidateOCO`: two reduce-only siblings, same size, side and expiry."""
    orders = self.orders
    if len(orders) != 2:
      fail(ERR_GROUP_SIZE_INVALID)
    if orders[0].base_amount != orders[1].base_amount:
      fail('BaseAmounts should be equal')
    if orders[0].is_ask != orders[1].is_ask:
      fail(ERR_IS_ASK_INVALID)
    if orders[0].reduce_only != 1 or orders[1].reduce_only != 1:
      fail(ERR_REDUCE_ONLY_INVALID)
    if orders[0].order_expiry != orders[1].order_expiry:
      fail(ERR_ORDER_EXPIRY_INVALID)
    check_sibling_orders(orders)

  def check_oto(self):
    """Go `ValidateOTO`: a primary and one opposite-side child with no size of its own."""
    orders = self.orders
    if len(orders) != 2:
      fail(ERR_GROUP_SIZE_INVALID)
    if orders[1].base_amount != 0:
      fail('BaseAmount should be nil')
    if orders[0].is_ask == orders[1].is_ask:
      fail(ERR_IS_ASK_INVALID)
    if orders[0].order_expiry != 0 and orders[0].order_expiry != orders[1].order_expiry:
      fail(ERR_ORDER_EXPIRY_INVALID)
    check_parent_order(orders[0])
    check_child_order(orders[1])

  def check_otoco(self):
    """Go `ValidateOTOCO`: a primary and an opposite-side stop-loss/take-profit pair."""
    orders = self.orders
    if len(orders) != 3:
      fail(ERR_GROUP_SIZE_INVALID)
    if orders[1].base_amount != 0 or orders[2].base_amount != 0:
      fail('BaseAmount should be nil')
    if orders[0].is_ask == orders[1].is_ask or orders[0].is_ask == orders[2].is_ask:
      fail(ERR_IS_ASK_INVALID)
    if orders[1].order_expiry != orders[2].order_expiry:
      fail(ERR_ORDER_EXPIRY_INVALID)
    if orders[0].order_expiry != 0 and orders[0].order_expiry != orders[1].order_expiry:
      fail(ERR_ORDER_EXPIRY_INVALID)
    check_parent_order(orders[0])
    check_sibling_orders(orders[1:])

  def body_elements(self) -> list[int]:
    """Grouping type, then the 4-element fold of the orders' hashes."""
    aggregated: HashOut = (0, 0, 0, 0)
    for i, order in enumerate(self.orders):
      aggregated = order.hash() if i == 0 else hash_two_to_one(aggregated, order.hash())
    return [self.grouping_type, *aggregated]

  def body_json(self) -> dict[str, Any]:
    """Grouping type and the orders."""
    return {
      'GroupingType': self.grouping_type,
      'Orders': [order.to_json() for order in self.orders],
    }
