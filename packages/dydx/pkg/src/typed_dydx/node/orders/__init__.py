"""dYdX node order helpers."""

from dataclasses import dataclass

from typed_dydx.node.context import NodeContext
from typed_dydx.node.orders.batch_cancel_orders import BatchCancelOrders
from typed_dydx.node.orders.cancel_order import CancelOrder
from typed_dydx.node.orders.place_order import PlaceOrder, PlacedOrder, PlacedOrders
from typed_dydx.node.orders.types import (
  ConditionType,
  Flags,
  OrderParams,
  OrderPlacement,
  Side,
  TimeInForce,
)
from typed_dydx.node.tx import Tx

@dataclass
class Orders(
  PlaceOrder,
  CancelOrder,
  BatchCancelOrders,
):
  """Composed order helper surface."""

  context: NodeContext
  """Shared node context used for wallet and chain access."""
  tx: Tx
  """Transaction helper used for signing and broadcasting."""
