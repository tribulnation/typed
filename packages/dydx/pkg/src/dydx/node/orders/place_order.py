"""dYdX order placement helper."""

import random
from dataclasses import dataclass

from typed_core.exceptions import BadRequest
from typing_extensions import Sequence

from dydx.node.constants import SHORT_BLOCK_WINDOW, STATEFUL_ORDER_TIME_WINDOW
from dydx.node.context import NodeContext
from dydx.indexer.types.market import PerpetualMarket
from dydx.node.market import Market
from dydx.node.tx import Tx
from dydx.node.orders.types import (
  ConditionType,
  Flags,
  OrderParams,
  OrderPlacement,
  Side,
  TimeInForce,
)
from dydx.protos.cosmos.tx import v1beta1 as tx_proto
from dydx.protos.dydxprotocol import clob

def random_client_id() -> int:
  """Generate a dYdX client order ID.

  Returns:
    Random client order ID in the dYdX accepted range.
  """
  return random.randint(0, 100_000_000)

def parse_flags(flags: Flags) -> int:
  """Convert order flags into protocol flag bits.

  Args:
    flags: Ergonomic order flag value.

  Returns:
    Integer order flag expected by dYdX CLOB order IDs.
  """
  match flags:
    case 'SHORT_TERM':
      return 0
    case 'LONG_TERM':
      return 64
    case 'CONDITIONAL':
      return 32

def parse_side(side: Side) -> clob.OrderSide:
  """Convert order side into the protocol enum.

  Args:
    side: Ergonomic order side value.

  Returns:
    dYdX protocol order side enum.
  """
  match side:
    case 'BUY':
      return clob.OrderSide(1)
    case 'SELL':
      return clob.OrderSide(2)

def parse_time_in_force(time_in_force: TimeInForce | None) -> clob.OrderTimeInForce:
  """Convert time in force into the protocol enum.

  Args:
    time_in_force: Ergonomic time-in-force value.

  Returns:
    dYdX protocol time-in-force enum.
  """
  match time_in_force:
    case 'IMMEDIATE_OR_CANCEL':
      return clob.OrderTimeInForce(1)
    case 'POST_ONLY':
      return clob.OrderTimeInForce(2)
    case 'FILL_OR_KILL':
      return clob.OrderTimeInForce(3)
    case _:
      return clob.OrderTimeInForce(0)

def parse_condition_type(condition_type: ConditionType | None) -> clob.OrderConditionType:
  """Convert condition type into the protocol enum.

  Args:
    condition_type: Ergonomic conditional order type.

  Returns:
    dYdX protocol order condition enum.
  """
  match condition_type:
    case 'TAKE_PROFIT':
      return clob.OrderConditionType(2)
    case 'STOP_LOSS':
      return clob.OrderConditionType(1)
    case _:
      return clob.OrderConditionType(0)

@dataclass
class PlacedOrder:
  """Result of a placed order."""

  tx: tx_proto.BroadcastTxResponse
  """Transaction broadcast response returned by the chain."""
  order: clob.Order
  """Protocol order message that was signed and submitted."""

@dataclass
class PlacedOrders:
  """Result of a multi-order placement transaction."""

  tx: tx_proto.BroadcastTxResponse
  """Transaction broadcast response returned by the chain."""
  orders: list[clob.Order]
  """Protocol order messages that were signed and submitted."""

@dataclass
class PlaceOrder:
  """Order placement endpoint."""

  context: NodeContext
  """Shared node context used for wallet and chain access."""
  tx: Tx
  """Transaction helper used for signing and broadcasting."""

  async def default_good_til(self, flags: Flags) -> tuple[int | None, int | None]:
    """Resolve default order expiry for an order flag.

    Args:
      flags: Order flag determining whether expiry is block-based or
        timestamp-based.

    Returns:
      Pair of `good_til_block` and `good_til_block_time` values. One side of
      the pair is populated depending on the order type.

    Raises:
      BadRequest: Raised when latest block metadata needed for expiry is
        unavailable.
    """
    latest_block = await self.context.chain.tendermint.get_latest_block()
    block = latest_block.block
    if block is None or block.header is None:
      raise BadRequest('Latest block response did not include a block header')
    if flags == 'SHORT_TERM':
      return block.header.height + SHORT_BLOCK_WINDOW, None
    if flags in {'LONG_TERM', 'CONDITIONAL'}:
      if block.header.time is None:
        raise BadRequest('Latest block response did not include block time')
      return None, int(block.header.time.timestamp()) + STATEFUL_ORDER_TIME_WINDOW
    return None, None

  async def build_order(
    self,
    *,
    market: Market | PerpetualMarket,
    order: OrderParams,
    subaccount: int = 0,
    good_til_block: int | None = None,
    good_til_block_time: int | None = None,
  ) -> clob.Order:
    """Build a protocol order without broadcasting it.

    Args:
      market: Market metadata used to convert price and size into protocol
        subticks and quantums.
      order: Ergonomic order parameters for the CLOB message.
      subaccount: dYdX subaccount number owned by the wallet.
      good_til_block: Optional explicit short-term expiry block.
      good_til_block_time: Optional explicit stateful expiry timestamp.

    Returns:
      dYdX protocol order message.
    """
    wallet = self.context.require_wallet()
    market_info = Market.from_payload(market)
    flags = order['flags']
    if good_til_block is None and good_til_block_time is None:
      good_til_block = order.get('good_til_block')
      good_til_block_time = order.get('good_til_block_time')
    if good_til_block is None and good_til_block_time is None:
      good_til_block, good_til_block_time = await self.default_good_til(flags)
    client_id = order.get('client_id') or random_client_id()
    order_id = market_info.order_id(
      owner=wallet.address,
      subaccount_number=subaccount,
      client_id=client_id,
      order_flags=parse_flags(flags),
    )
    return clob.Order(
      order_id=order_id,
      side=parse_side(order['side']),
      quantums=market_info.calculate_quantums(order['size']),
      subticks=market_info.calculate_subticks(order['price']),
      good_til_block=good_til_block,
      good_til_block_time=good_til_block_time,
      time_in_force=parse_time_in_force(order.get('time_in_force')),
      reduce_only=order.get('reduce_only', False),
      client_metadata=order.get('client_metadata', 0),
      condition_type=parse_condition_type(order.get('condition_type')),
      conditional_order_trigger_subticks=order.get('conditional_order_trigger_subticks', 0),
    )

  async def place_order(
    self,
    market: Market | PerpetualMarket,
    *,
    order: OrderParams,
    subaccount: int = 0,
    mode: tx_proto.BroadcastMode = tx_proto.BroadcastMode(2),
    simulate: bool = False,
  ) -> PlacedOrder:
    """Build, sign, and broadcast a long-term dYdX order.

    Args:
      market: Market metadata used to convert price and size into protocol
        subticks and quantums. Accepts either a prepared `Market` or the
        indexer `PerpetualMarket` payload.
      order: Order parameters for the CLOB message. dYdX only allows batched
        placement for stateful long-term or conditional orders.
      subaccount: dYdX subaccount number owned by the wallet.
      mode: Cosmos broadcast mode.
      simulate: Whether to simulate the transaction instead of broadcasting it.

    Returns:
      The broadcast response and protocol order that was signed.
    """
    order_message = await self.build_order(
      market=market,
      order=order,
      subaccount=subaccount,
    )
    response = await self.tx.sign_and_broadcast(
      [clob.MsgPlaceOrder(order=order_message)],
      mode=mode,
      simulate=simulate,
    )
    return PlacedOrder(tx=response, order=order_message)

  async def place_orders(
    self,
    orders: Sequence[OrderPlacement],
    *,
    mode: tx_proto.BroadcastMode = tx_proto.BroadcastMode(2),
    simulate: bool = False,
  ) -> PlacedOrders:
    """Build, sign, and broadcast multiple stateful dYdX orders.

    dYdX rejects transactions containing multiple short-term `MsgPlaceOrder`
    messages. This helper only accepts long-term or conditional orders, which
    are stateful and can be submitted together in one transaction.

    Args:
      orders: Order placement items. Each item carries its market metadata,
        order parameters, and optional subaccount number.
      mode: Cosmos broadcast mode.
      simulate: Whether to simulate the transaction before broadcasting.

    Returns:
      The broadcast response and protocol orders that were signed.

    Raises:
      BadRequest: Raised when no orders are supplied or any order is short-term.
    """
    if not orders:
      raise BadRequest('At least one order is required')
    if any(item['order']['flags'] == 'SHORT_TERM' for item in orders):
      raise BadRequest('place_orders only supports long-term or conditional orders')
    order_messages = [
      await self.build_order(
        market=item['market'],
        order=item['order'],
        subaccount=item.get('subaccount', 0),
      )
      for item in orders
    ]
    response = await self.tx.sign_and_broadcast(
      [clob.MsgPlaceOrder(order=order) for order in order_messages],
      mode=mode,
      simulate=simulate,
    )
    return PlacedOrders(tx=response, orders=order_messages)
