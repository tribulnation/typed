"""dYdX node order helpers."""

from dataclasses import dataclass

from dydx.node.context import NodeContext
from dydx.node.orders.batch_cancel_orders import BatchCancelOrders
from dydx.node.orders.cancel_order import CancelOrder
from dydx.node.orders.place_order import PlaceOrder, PlacedOrder, PlacedOrders
from dydx.node.orders.types import (
  ConditionType,
  Flags,
  OrderParams,
  OrderPlacement,
  Side,
  TimeInForce,
)
from dydx.node.tx import Tx

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
